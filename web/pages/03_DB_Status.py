import streamlit as st
from components import auth, session

st.set_page_config(page_title="DB Status", page_icon="🗄️", layout="wide")

session.init_session_state()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin"])

st.title("DB Status")
st.info("Page not implemented yet.")
