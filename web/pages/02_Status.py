import streamlit as st
from components import auth, session

st.set_page_config(page_title="Status", page_icon="🔄", layout="wide")

session.init_session_state()
auth.require_role(["admin", "visitor"])

st.title("Status")
st.info("Page not implemented yet.")
