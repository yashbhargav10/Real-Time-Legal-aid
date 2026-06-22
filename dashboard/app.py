import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8081")
API_KEY = os.getenv("API_KEY", "your-secure-api-key")

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.set_page_config(page_title="Real-Time Legal Aid", page_icon="⚖️", layout="centered")

st.title("⚖️ Real-Time Legal Aid Assistant")
st.markdown("Ask me questions about Indian Labour Rights, Tenant Rights, and Consumer Disputes.")

# Display Chat History
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if query := st.chat_input("What is your legal question?"):
    # Add User Message
    st.session_state["messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    # Generate Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
            payload = {
                "session_id": st.session_state["session_id"],
                "query": query
            }
            
            response = requests.post(f"{API_URL}/query", json=payload, headers=headers)
            response.raise_for_status()
            
            answer = response.json().get("answer", "No answer received.")
            message_placeholder.markdown(answer)
            
            # Save Assistant Message
            st.session_state["messages"].append({"role": "assistant", "content": answer})
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error communicating with the API: {e}"
            message_placeholder.error(error_msg)
            st.session_state["messages"].append({"role": "assistant", "content": error_msg})
