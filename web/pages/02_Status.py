import streamlit as st
from components import auth, session, layout, agents
import pandas as pd

st.set_page_config(page_title="Status", page_icon="🔄", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin", "visitor"])

layout.render_header("System & Agents Status")

st.title("System & Agents Status")

st.markdown("---")

st.subheader("🤖 Agent Heartbeat")

try:
    agent_data = agents.get_agent_overview()
    
    if agent_data:
        df = pd.DataFrame(agent_data)
        df.columns = ["Agent", "Status", "Last Heartbeat", "Queue Size", "Details"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No agent data available. Agents may not be running yet.")
except Exception as e:
    st.error("⚠️ Unable to retrieve agent status. Database or agents may be offline.")
    st.info("This is normal if agents are starting up or running on a different server.")
    with st.expander("Error Details"):
        st.code(str(e))

st.markdown("---")

st.subheader("💻 System Health (Coming soon)")
st.info("CPU/RAM/Disk metrics from system_health table will appear here.")
