import streamlit as st
from components import auth, session

st.set_page_config(page_title="Trace", page_icon="🔍", layout="wide")

session.init_session_state()
auth.require_role(["admin", "visitor"])

st.title("Trace")
st.info("Page not implemented yet.")
