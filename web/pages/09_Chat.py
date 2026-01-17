import streamlit as st
from components import auth, session, layout
import requests
import os
import json

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin", "visitor"])

layout.render_header("AI ")

st.title("💬 Chat with Ollama")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Get Ollama API base URL
ollama_base = os.getenv('OLLAMA_API_BASE', os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))

# Check Ollama availability
try:
    response = requests.get(f"{ollama_base}/api/tags", timeout=2)
    ollama_available = response.status_code == 200
    models = response.json().get('models', []) if ollama_available else []
except Exception as e:
    ollama_available = False
    models = []
    st.error(f"⚠️ Cannot connect to Ollama server at {ollama_base}")
    st.info("Make sure Ollama is running on Linux 2")
    with st.expander("Error Details"):
        st.code(str(e))

if ollama_available:
    st.success(f"✅ Connected to Ollama at {ollama_base}")
    
    # Model selector
    if models:
        model_names = [m['name'] for m in models]
        selected_model = st.selectbox("Select Model", model_names, index=0)
    else:
        st.warning("No models found. Please pull a model first.")
        st.code("ollama pull llama3")
        st.stop()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call Ollama API
                    response = requests.post(
                        f"{ollama_base}/api/generate",
                        json={
                            "model": selected_model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        assistant_response = result.get('response', 'No response')
                        st.markdown(assistant_response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_response
                        })
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.code(response.text)
                
                except Exception as e:
                    st.error(f"Failed to get response: {str(e)}")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

else:
    st.warning("Chat is not available. Ollama server is offline.")
    st.info("Please ensure Ollama is running on Linux 2 and accessible.")
