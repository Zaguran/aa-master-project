import streamlit as st
from components import auth, session

st.set_page_config(page_title="TableView", page_icon="📋", layout="wide")

session.init_session_state()
auth.require_role(["admin"])

st.title("TableView")
st.info("Page not implemented yet.")
