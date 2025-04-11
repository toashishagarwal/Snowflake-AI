from openai import OpenAI
import snowflake.connector
import pandas as pd
import json
import os
import time

# Configuration - Replace with your actual credentials
SNOWFLAKE_CONFIG = {
    "account": "<YOUR_ACC>",
    "user": "<YOUR_USER>",
    "password": "<YOUR_PASSWORD>",
    "role": "<YOUR_ROLE>",
    "warehouse": "<YOUR_WH>",
    "database": "<YOUR_DB>",
    "schema": "<YOUR_SCHEMA>"
}

# Schema cache settings
SCHEMA_CACHE_FILE = "schema_cache.json"
CACHE_EXPIRY_DAYS = 7  # How many days before refreshing the schema cache

OPENAI_API_KEY = "<YOUR_API_KEY>"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def connect_to_snowflake():
    """Establish connection to Snowflake"""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_CONFIG["user"],
            password=SNOWFLAKE_CONFIG["password"],
            account=SNOWFLAKE_CONFIG["account"],
            warehouse=SNOWFLAKE_CONFIG["warehouse"],
            database=SNOWFLAKE_CONFIG["database"],
            schema=SNOWFLAKE_CONFIG["schema"],
            role=SNOWFLAKE_CONFIG["role"]
        )
        print("Connected to Snowflake successfully!")
        return conn
    except Exception as e:
        print(f"Failed to connect to Snowflake: {e}")
        return None

def fetch_database_schema(conn):
    """Fetch schema information from database"""
    cur = conn.cursor()
    
    # Get tables in current schema
    cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = CURRENT_SCHEMA()
    """)
    tables = cur.fetchall()
    
    schema_info = []
    for table in tables:
        table_name = table[0]
        
        # Get columns for each table
        cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' AND table_schema = CURRENT_SCHEMA()
        """)
        columns = cur.fetchall()
        
        table_info = f"Table: {table_name}\nColumns:"
        for col in columns:
            table_info += f"\n  - {col[0]} ({col[1]})"
        
        schema_info.append(table_info)
    
    cur.close()
    return "\n\n".join(schema_info)

def get_database_schema(conn):
    """Get database schema info with caching"""
    # Check if cache file exists and is recent
    if os.path.exists(SCHEMA_CACHE_FILE):
        with open(SCHEMA_CACHE_FILE, 'r') as f:
            try:
                cache_data = json.load(f)
                cache_timestamp = cache_data.get('timestamp', 0)
                schema_info = cache_data.get('schema', '')
                
                # Check if cache is still valid (not expired)
                cache_age_days = (time.time() - cache_timestamp) / (60 * 60 * 24)
                if cache_age_days < CACHE_EXPIRY_DAYS and schema_info:
                    print(f"Using cached schema (age: {cache_age_days:.1f} days)")
                    return schema_info
            except (json.JSONDecodeError, KeyError):
                # Handle corrupted cache file
                print("Cache file corrupted, will fetch fresh schema")
    
    # If no valid cache, fetch schema from database
    print("Fetching fresh schema from database...")
    schema_info = fetch_database_schema(conn)
    
    # Save to cache
    cache_data = {
        'timestamp': time.time(),
        'schema': schema_info
    }
    
    with open(SCHEMA_CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)
    
    return schema_info

def get_relevant_schema(conn, user_query, full_schema_info=None):
    """Extract only relevant tables based on user query"""
    # If no full schema available, get it
    if not full_schema_info:
        full_schema_info = get_database_schema(conn)
    
    # Get all table names from schema
    table_names = []
    for line in full_schema_info.split("\n"):
        if line.startswith("Table:"):
            table_name = line.split("Table:")[1].strip()
            table_names.append(table_name)
    
    # Ask OpenAI which tables might be relevant to this query
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using smaller model for this task
            messages=[
                {"role": "system", "content": "You are a database expert. Given a query and list of tables, identify which tables are relevant to the query. Reply ONLY with comma-separated table names, nothing else."},
                {"role": "user", "content": f"Given these tables: {', '.join(table_names)}\nWhich tables are needed to answer this query: {user_query}\nReply ONLY with relevant table names separated by commas, nothing else."}
            ]
        )
        
        relevant_tables = response.choices[0].message.content.strip().split(',')
        relevant_tables = [t.strip() for t in relevant_tables]
        
        # Extract schema for only relevant tables
        relevant_schema = []
        current_table = None
        collect = False
        
        for line in full_schema_info.split("\n"):
            if line.startswith("Table:"):
                current_table = line.split("Table:")[1].strip()
                collect = current_table in relevant_tables
                if collect:
                    relevant_schema.append(line)
            elif collect and line.strip():
                relevant_schema.append(line)
        
        return "\n".join(relevant_schema)
    except Exception as e:
        print(f"Error filtering schema: {e}")
        # Fall back to returning a truncated version of the full schema
        return "\n".join(full_schema_info.split("\n")[:100]) + "\n...(schema truncated)"


def english_to_sql(query, schema_info):
    """Convert English query to SQL using OpenAI"""
    prompt = f"""
    Based on the following database schema:
    
    {schema_info}
    
    Convert this English question into a SQL query for Snowflake:
    "{query}"
    
    Return ONLY the SQL query with no additional text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use the appropriate model for your subscription
            messages=[
                {"role": "system", "content": "You are a SQL expert that converts English questions into correct Snowflake SQL queries. Only respond with the SQL query."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        sql_query_raw = response.choices[0].message.content.strip()
        sql_query = extract_sql_query(sql_query_raw)
        return sql_query
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def extract_sql_query(text):
    # Look for content between SQL code fences
    import re
    sql_pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(sql_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return None


def execute_query(conn, sql_query):
    """Execute SQL query and return results"""
    try:
        cur = conn.cursor()
        
        cur.execute(sql_query)
        results = cur.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cur.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=column_names)
        cur.close()
        return df
    except Exception as e:
        return f"Error executing query: {str(e)}"

def validate_sql_against_schema(sql_query, schema_cache):
    """
    Validates and corrects a SQL query against the cached schema.
    
    Args:
        sql_query (str): The SQL query to validate
        schema_cache (dict): Dictionary mapping table names to lists of column names
                             Format: {'TABLE_NAME': ['COL1', 'COL2', ...]}
    
    Returns:
        tuple: (corrected_query, corrections_made)
            - corrected_query: The SQL query with corrected column names
            - corrections_made: List of corrections made (for logging/debugging)
    """
    import re
    from difflib import get_close_matches
    
    corrections_made = []
    corrected_query = sql_query
    
    # Extract table names from the query
    # This is a simplified approach - production code might need a proper SQL parser
    table_pattern = re.compile(r'\bFROM\s+([^\s,;()]+)|JOIN\s+([^\s,;()]+)', re.IGNORECASE)
    table_matches = table_pattern.findall(sql_query)
    tables = [match[0] or match[1] for match in table_matches]
    
    # Extract all possible column references
    # This regex finds words that might be column names
    word_pattern = re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)\b')
    words = word_pattern.findall(sql_query)
    
    # Get all actual columns from referenced tables
    all_columns = []
    for table in tables:
        table_upper = table.upper()
        if table_upper in schema_cache:
            #all_columns.extend(schema_cache[table_upper])
            pattern = rf"Table:\s*{re.escape(table_upper)}\s*Columns:\s*((?:\s*-\s+[^\n]+\n?)*)"
            match = re.search(pattern, schema_cache)
            if not match:
                return []

            columns_block = match.group(1)

            # Extract individual column names using another regex
            all_columns =  re.findall(r"-\s+([^\s(]+)", columns_block)
    
    # Create variations of actual columns for matching
    column_variations = {}
    for col in all_columns:
        # Original column name
        column_variations[col] = col
        
        # Underscored version (PRIMARYLOCATIONTYPE -> PRIMARY_LOCATION_TYPE)
        underscored = re.sub(r'([a-z])([A-Z])', r'\1_\2', col)
        if underscored != col:
            column_variations[underscored] = col
        
        # No underscore version (PRIMARY_LOCATION_TYPE -> PRIMARYLOCATIONTYPE)
        no_underscore = col.replace('_', '')
        if no_underscore != col:
            column_variations[no_underscore] = col
    
    # Check each word in the query against our column variations
    for word in words:
        word_upper = word.upper()
        # If the word exists as a variation but isn't the canonical form
        if word_upper in column_variations and word_upper != column_variations[word_upper]:
            canonical = column_variations[word_upper]
            # Replace the word with proper casing preserved
            pattern = re.compile(r'\b' + re.escape(word) + r'\b')
            corrected_query = pattern.sub(canonical, corrected_query)
            corrections_made.append(f"Changed '{word}' to '{canonical}'")
        # Try fuzzy matching for words that don't match exactly
        elif word_upper not in all_columns:
            # Get close matches with a cutoff of 0.8 similarity
            matches = get_close_matches(word_upper, all_columns, n=1, cutoff=0.8)
            if matches:
                # Replace the word with the close match
                pattern = re.compile(r'\b' + re.escape(word) + r'\b')
                corrected_query = pattern.sub(matches[0], corrected_query)
                corrections_made.append(f"Changed '{word}' to '{matches[0]}' (fuzzy match)")
    
    return corrected_query, corrections_made

# Example usage:
def validate_snowflake_sql(sql_query, schema_cache):
    """
    Wrapper function to validate and correct Snowflake SQL, with error handling.
    
    Args:
        sql_query (str): The SQL query to validate
        schema_cache (dict): Dictionary mapping table names to lists of column names
    
    Returns:
        tuple: (corrected_query, success, message)
    """
    try:
        corrected_query, corrections = validate_sql_against_schema(sql_query, schema_cache)
        print("corrected_query-->", corrected_query)
        if corrections:
            return corrected_query, True, f"Query corrected: {', '.join(corrections)}"
        return sql_query, True, "No corrections needed"
    except Exception as e:
        return sql_query, False, f"Error validating SQL: {str(e)}"

def explain_sql(sql_query):
    """Generate an explanation of the SQL query"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Using a smaller model for explanations
            messages=[
                {"role": "system", "content": "You are a helpful SQL expert. Explain the following SQL query in simple terms."},
                {"role": "user", "content": f"Explain this SQL query in simple terms: {sql_query}"}
            ]
        )
        
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

def main():
    """Main function to run the chatbot"""
    print("Snowflake OpenAI SQL Chatbot")
    print("==========================")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    # Get schema information
    print("\nRetrieving database schema...")
    schema_info = get_database_schema(conn)
    print("Schema retrieved successfully!")
    
    # Main interaction loop
    while True:
        print("\n" + "-"*50)
        user_query = input("\nAsk a question about your data (or type 'quit' to exit): ")
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            break

        # Get only relevant schema for this query
        print("Analyzing relevant tables...")
        relevant_schema = get_relevant_schema(conn, user_query, schema_info)
        
        # Convert to SQL
        print("\nTranslating to SQL...")
        sql_query = english_to_sql(user_query, schema_info)
        print("\nGenerated SQL Query:")
        print("-"*50)
        print(sql_query)
        print("-"*50)
        
        # Execute the query if valid
        if sql_query and not sql_query.startswith("Error"):
            print("\nExecuting query...")
            results = execute_query(conn, sql_query)

            if isinstance(results, str) and results.startswith("Error executing query:"):
                # try validating the sql against the cached schema & autocorrect
                corrected_sql, success, message = validate_snowflake_sql(sql_query, schema_info)
               
                if not success:
                    return f"Error: {message}"
                
                results = execute_query(conn, corrected_sql)
            
            if isinstance(results, pd.DataFrame):
                print("\nQuery Results:")
                print("-"*50)
                print(results)
                print("-"*50)
                
                # Generate explanation
                print("\nGenerating explanation...")
                explanation = explain_sql(sql_query)
                print("\nExplanation:")
                print("-"*50)
                print(explanation)
                print("-"*50)
            else:
                print(results)
        else:
            print(sql_query)
    
    # Close connection
    conn.close()
    print("\nConnection closed. Goodbye!")

if __name__ == "__main__":
    main()
