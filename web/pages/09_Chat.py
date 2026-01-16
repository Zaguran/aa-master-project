import streamlit as st
from components import auth, session, utils

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

session.init_session_state()

if not auth.is_authenticated():
    st.switch_page("pages/00_Login.py")

auth.require_role(["admin"])

st.title("Chat (Type A)")

st.markdown("### Simple Chat Interface")
st.markdown("Ask a question and receive an answer. No history, no database logging.")

user_question = st.text_input(
    "Your Question",
    placeholder="Type your question here...",
    help="Enter a question to send to the chat endpoint"
)

if st.button("Send", type="primary", use_container_width=True):
    if user_question.strip():
        with st.spinner("Processing..."):
            response = utils.chat_simple(user_question)
        
        st.text_area(
            "Answer",
            value=response,
            height=150,
            disabled=True
        )
    else:
        st.warning("Please enter a question first.")
