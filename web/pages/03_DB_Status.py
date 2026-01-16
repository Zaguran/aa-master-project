import streamlit as st
from components import auth, session

st.set_page_config(page_title="DB Status", page_icon="🗄️", layout="wide")

session.init_session_state()
auth.require_role(["admin"])

st.title("DB Status")
st.info("Page not implemented yet.")
