import streamlit as st
from components import auth, session

st.set_page_config(page_title="Reports", page_icon="📄", layout="wide")

session.init_session_state()

if not auth.is_authenticated():
    st.switch_page("pages/00_Login.py")

auth.require_role(["admin"])

st.title("Reports")
st.info("Page not implemented yet.")
