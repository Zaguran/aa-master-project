import streamlit as st
from components import auth, session, layout
import database
import pandas as pd

st.set_page_config(page_title="Table View", page_icon="📋", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Table View")

st.title("Table View")

AVAILABLE_TABLES = [
    "customer",
    "projects",
    "nodes",
    "links",
    "ai_analysis",
    "ai_embedding_model",
    "req_embedding",
    "req_match",
    "platform_trace",
    "code_change_event",
    "code_impact",
    "code_link_hint",
    "rfq",
    "rfq_report",
    "agent_status",
    "system_health"
]

if "table_offset" not in st.session_state:
    st.session_state.table_offset = 0

if "selected_table" not in st.session_state:
    st.session_state.selected_table = AVAILABLE_TABLES[0]

selected_table = st.selectbox(
    "Select table to view:",
    AVAILABLE_TABLES,
    index=AVAILABLE_TABLES.index(st.session_state.selected_table)
)

if selected_table != st.session_state.selected_table:
    st.session_state.selected_table = selected_table
    st.session_state.table_offset = 0
    st.rerun()

st.markdown("---")

LIMIT = 50
offset = st.session_state.table_offset

rows, total = database.get_table_data(selected_table, limit=LIMIT, offset=offset)

if isinstance(rows, str):
    st.error(f"Error loading table data: {rows}")
else:
    st.info(f"**Table:** `{selected_table}` | **Total rows:** {total} | **Showing:** {offset + 1} - {min(offset + LIMIT, total)}")
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No data available in this table.")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=(offset == 0), use_container_width=True):
            st.session_state.table_offset = max(0, offset - LIMIT)
            st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page {(offset // LIMIT) + 1} of {(total // LIMIT) + 1}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️", disabled=(offset + LIMIT >= total), use_container_width=True):
            st.session_state.table_offset = offset + LIMIT
            st.rerun()
