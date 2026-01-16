import streamlit as st
from components import auth, session

st.set_page_config(page_title="Status", page_icon="🔄", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin", "visitor"])

st.title("Status")
st.info("Page not implemented yet.")
