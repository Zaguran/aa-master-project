import streamlit as st
from components import auth, session, layout
import database
import pandas as pd

st.set_page_config(page_title="DB Status", page_icon="🗄️", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Database Status")

st.title("Database Status")
st.info("Overview of tables in schema 'work_aa'.")

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col2:
    if st.button("📦 DB Extensions", use_container_width=True, disabled=True):
        st.info("Feature coming soon")

with col3:
    if st.button("💾 Storage Size", use_container_width=True, disabled=True):
        st.info("Feature coming soon")

st.markdown("---")

stats = database.get_aa_stats()

if stats:
    df = pd.DataFrame(stats)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No data available or database connection error.")
