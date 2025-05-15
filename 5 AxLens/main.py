import streamlit as st # Import python packages
from snowflake.snowpark.context import get_active_session

from snowflake.core import Root

import pandas as pd
import json
import re

pd.set_option("max_colwidth",None)

### Default Values
NUM_CHUNKS = 3 # Num-chunks provided as context. Play with this to check how it affects your accuracy

# service parameters
CORTEX_SEARCH_DATABASE = "RESEARCH"
CORTEX_SEARCH_SCHEMA = "AAGARWAL"
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"
######

# columns to query in the service
COLUMNS = [
    "chunk",
    "chunk_index",
    "relative_path",
    "category"
]

session = get_active_session()

root = Root(session)                         

svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
   
### Functions
     
def config_options():
    st.sidebar.selectbox('Select your model:',('mistral-large2', 'llama3.1-70b',
                        'llama3.1-8b', 'snowflake-arctic'), key="model_name")

    categories = session.sql("select category from docs_chunks_table group by category").collect()

    cat_list = ['ALL']
    for cat in categories:
        cat_list.append(cat.CATEGORY)
            
    st.sidebar.selectbox('Select what products you are looking for', cat_list, key = "category_value")

    st.sidebar.expander("Session State").write(st.session_state)

def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)
    else: 
        filter_obj = {"@eq": {"category": st.session_state.category_value} }
        response = svc.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)

    st.sidebar.json(response.json())   
    return response.json()  

def create_prompt (myquestion):

    if st.session_state.rag == 1:
        prompt_context = get_similar_chunks_search_service(myquestion)
  
        prompt = f"""
           You are an expert chat assistance that extracs information from the CONTEXT provided
           between <context> and </context> tags.
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. If there are companies mentioned include that in your answer.
           Provide your answer in short bullet point on anything related to Patient Preferences, Cost and Pricing, 
           Market Dynamics and Safety and Efficacy.
           If you don´t have the information just say so.
           Only anwer the question if you can extract it from the CONTEXT provided.
           
           Do not mention the CONTEXT used in your answer.
    
           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
           """

        json_data = json.loads(prompt_context)
        relative_paths = set(item['relative_path'] for item in json_data['results'])
        
    else:     
        prompt = f"""[0]
         'Question:  
           {myquestion} 
           Answer: '
           """
        relative_paths = "None"
            
    return prompt, relative_paths

def complete(myquestion):
    prompt, relative_paths = create_prompt (myquestion)
    cmd = """
            select snowflake.cortex.complete(?, ?) as response
          """
    
    df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    return df_response, relative_paths

def main():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;800&family=Inter:wght@300;600&display=swap');
    
    .axlens-container {
        text-align: center;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    .axlens-title {
        background: linear-gradient(120deg, #3a0ca3, #4361ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 30px;
    }
    
    .axlens-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-style: normal;
        font-weight: 300;
        color: #6c757d;
        margin-top: 0px;
    }
    </style>
    
    <div class="axlens-container">
        <div class="axlens-title">🧬 AxLens</div>
        <div class="axlens-subtitle">Your AI-Powered Lens into Aesthetics News</div>
    </div>
    """, unsafe_allow_html=True)

    docs_available = session.sql("ls @mednews").collect()

    # Below section can be enabled if you want to see the list of documents
    #############################################
    # list_docs = []
    # for doc in docs_available:
    #            list_docs.append(doc["name"])
    # st.dataframe(list_docs)
    #############################################

    config_options()

    st.session_state.rag = st.sidebar.checkbox('Use your own documents as context?')

    st.markdown("""
    <style>
    .question-box {
        background-color: #f1f3f5;
        border-radius: 12px;
        padding: 1rem;
        font-size: 16px;
        border: none;
        width: 100%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    question = st.text_input("Enter question", placeholder="🔍 Ask about a healthcare side effect, breakthrough, or drug...", key="query_input")

    if question:
        response, relative_paths = complete(question)
        res_text = response[0].RESPONSE
        #st.markdown(res_text)

        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600&display=swap');
        
        .section-tile {
            background-color: #f8f9fb;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            font-family: 'Manrope', sans-serif;
            margin-bottom: 20px;
            transition: transform 0.2s ease;
        }
        .section-tile:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #3a0ca3;
            margin-bottom: 10px;
        }
        .section-content {
            font-size: 15px;
            color: #212529;
            line-height: 1.6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        sections = parse_sections(res_text)

        for title, content in sections.items():
            # Replace dashes with bullets
            content = content.replace("- ", "•")
        
            st.markdown(f"""
            <div class="section-tile">
                <div class="section-title">{title}</div>
                <div class="section-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if relative_paths != "None":
            with st.sidebar.expander("Related Documents"):
                for path in relative_paths:
                    cmd2 = f"select GET_PRESIGNED_URL(@mednews, '{path}', 360) as URL_LINK from directory(@mednews)"
                    df_url_link = session.sql(cmd2).to_pandas()
                    url_link = df_url_link._get_value(0,'URL_LINK')
        
                    display_url = f"Doc: [{path}]({url_link})"
                    st.sidebar.markdown(display_url)
                
def parse_sections(text):
    new_text= text.replace('*', "")
    #new_text = text;
    # Match "Section Title:" → Group content under it
    pattern = re.compile(r'([A-Z][\w\s&]+:)[\r\n]+')
    parts = pattern.split(new_text.strip())  # Split by headings
    sections = {}

    i = 1
    while i < len(parts):
        title = parts[i].strip(":").strip()
        content = parts[i + 1].strip()
        sections[title] = content
        i += 2
    return sections


if __name__ == "__main__":
    main()
