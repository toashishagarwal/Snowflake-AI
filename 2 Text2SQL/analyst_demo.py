from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import snowflake.connector
import streamlit as st

DATABASE = "demo_db"
SCHEMA = "demo_schema"
STAGE = "demo_stage"
FILE = "demo_sm.yaml"
WAREHOUSE = "demo_wh"

# replace values below with your Snowflake connection information
HOST = "<YOUR_HOSTNAME>"
ACCOUNT = "<YOUR_ACCOUNT>"
USER = "<YOUR_USER>"
PASSWORD = "<YOUR_PASSWORD>"
ROLE = "<YOUR_ROLE>"

if 'CONN' not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        host=HOST,
        port=443,
        warehouse=WAREHOUSE,
        role=ROLE,
    )

# Configuration constants
if 'CONFIG' not in st.session_state:
    st.session_state.CONFIG = {
        'MAX_HISTORY': 5  # Default number of conversation turns to include in context
    }

def send_message(prompt: str) -> Dict[str, Any]:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }
   
    # Add context parameter if there's conversation history
    if len(st.session_state.messages) > 0:
        # Create a context string from previous interactions
        context = ""
        # Calculate how many conversation turns to include (each turn is a user+assistant pair)
        max_turns = st.session_state.CONFIG['MAX_HISTORY']
        
        # Calculate the starting index to get only the last N turns
        # Each turn has 2 messages (user + assistant)
        start_idx = max(0, len(st.session_state.messages) - (max_turns * 2))
        
        # Get the relevant conversation history
        history_messages = st.session_state.messages[start_idx:]
        
        # Build the context string from the history
        for i in range(0, len(history_messages), 2):
            if i < len(history_messages):
                user_msg = history_messages[i]
                if user_msg["role"] == "user" and user_msg["content"]:
                    context += f"User: {user_msg['content'][0]['text']}\n"
            
            if i + 1 < len(history_messages):
                assistant_msg = history_messages[i + 1]
                if assistant_msg["role"] == "assistant":
                    for content_item in assistant_msg["content"]:
                        if content_item["type"] == "text":
                            context += f"Assistant: {content_item['text']}\n"
        
        # Add context to the request if available
        if context:
            enhanced_prompt = f"Previous conversation:\n{context}\n\nCurrent question: {prompt}\n\nPlease answer the current question taking into account the previous conversation context."
            request_body["messages"][0]["content"][0]["text"] = enhanced_prompt
    
    resp = requests.post(
        url=f"https://{HOST}/api/v2/cortex/analyst/message",
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
            "Content-Type": "application/json",
        },
    )
    request_id = resp.headers.get("X-Snowflake-Request-Id")
    
    if resp.status_code < 400:
        return {**resp.json(), "request_id": request_id}  # type: ignore[arg-type]
    else:
        raise Exception(
            f"Failed request (id: {request_id}) with status {resp.status_code}: {resp.text}"
        )

def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            request_id = response["request_id"]
            content = response["message"]["content"]
            display_content(content=content, request_id=request_id)  # type: ignore[arg-type]
    st.session_state.messages.append(
        {"role": "assistant", "content": content, "request_id": request_id}
    )

def display_content(
    content: List[Dict[str, str]],
    request_id: Optional[str] = None,
    message_index: Optional[int] = None,
) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    if request_id:
        with st.expander("Request ID", expanded=False):
            st.markdown(request_id)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    df = pd.read_sql(item["statement"], st.session_state.CONN)
                    if len(df.index) > 1:
                        data_tab, line_tab, bar_tab = st.tabs(
                            ["Data", "Line Chart", "Bar Chart"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                        with line_tab:
                            st.line_chart(df)
                        with bar_tab:
                            st.bar_chart(df)
                    else:
                        st.dataframe(df)

st.title("****Text2SQL Chatbot****")
st.markdown(f"Semantic Model: `{FILE}`")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        display_content(
            content=message["content"],
            request_id=message.get("request_id"),
            message_index=message_index,
        )

if user_input := st.chat_input("What is your question?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None
