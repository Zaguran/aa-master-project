"""
Dashboard Page with System Metrics
Version: 1.8
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components import auth, session, layout

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/99_Login_Logout.py")
    st.stop()

auth.require_role(["admin", "visitor"])

layout.render_header("Dashboard")
st.title("📊 Dashboard")

st.success(f"Welcome, {user['full_name']}!")

st.markdown("---")
st.subheader("📈 System Overview")

# Get metrics from database
from agents.db_bridge.database import get_connection
from psycopg2.extras import RealDictCursor

try:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Count embeddings
    cur.execute("SELECT COUNT(*) as count FROM embeddings")
    embeddings_count = cur.fetchone()['count']

    # Count matches
    cur.execute("SELECT COUNT(*) as count FROM matches")
    matches_count = cur.fetchone()['count']

    # Count nodes (requirements only)
    cur.execute("SELECT COUNT(*) as count FROM nodes WHERE type='requirement'")
    requirements_count = cur.fetchone()['count']

    # Active agents (heartbeat within last 5 minutes)
    cur.execute("""
        SELECT COUNT(*) as count FROM agent_status
        WHERE last_heartbeat > NOW() - INTERVAL '5 minutes'
    """)
    active_agents = cur.fetchone()['count']

    cur.close()
    conn.close()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Requirements", requirements_count)
    with col2:
        st.metric("Embeddings", embeddings_count)
    with col3:
        st.metric("Matches", matches_count)
    with col4:
        st.metric("Active Agents", active_agents)

except Exception as e:
    st.error(f"Error loading metrics: {e}")

st.markdown("---")

st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📥 Import Data**")
    if st.button("Import Platform Requirements", key="btn_import_platform"):
        st.switch_page("pages/10_Import_Platform.py")
    if st.button("Import Customer Requirements", key="btn_import_customer"):
        st.switch_page("pages/11_Import_Customer.py")

with col2:
    st.markdown("**🤖 AI Processing**")
    if st.button("Generate Embeddings", key="btn_embeddings"):
        st.switch_page("pages/12_Embeddings.py")
    if st.button("Run Matching", key="btn_matching"):
        st.switch_page("pages/13_Matching.py")

with col3:
    st.markdown("**📊 Analysis**")
    if st.button("View Traceability", key="btn_trace"):
        st.switch_page("pages/14_Trace.py")
    if st.button("Check Status", key="btn_status"):
        st.switch_page("pages/80_Status.py")

st.markdown("---")

# Additional info
st.info("Use the navigation menu on the left to access all modules.")
