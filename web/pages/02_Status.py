import streamlit as st
from components import auth, session, layout, agents
import pandas as pd
import json

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


def render_resource_bar(value, label, color_thresholds=None):
    """Render a simple progress bar for resource usage."""
    if color_thresholds is None:
        color_thresholds = {"low": 50, "medium": 80}

    if value < color_thresholds["low"]:
        color = "#28a745"  # green
    elif value < color_thresholds["medium"]:
        color = "#ffc107"  # yellow
    else:
        color = "#dc3545"  # red

    bar_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <span style="width: 40px; font-size: 12px;">{label}</span>
        <div style="flex-grow: 1; background-color: #e0e0e0; border-radius: 4px; height: 16px; margin-left: 8px;">
            <div style="width: {min(value, 100)}%; background-color: {color}; height: 100%; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 10px; color: white; font-weight: bold;">{value:.1f}%</span>
            </div>
        </div>
    </div>
    """
    return bar_html


def parse_details(details):
    """Parse details field - handle both string and dict."""
    if details is None:
        return {}
    if isinstance(details, str):
        try:
            return json.loads(details)
        except:
            return {}
    return details


try:
    agent_data = agents.get_agent_overview()

    if agent_data:
        # Create columns for cards layout
        st.markdown("### Active Agents with Resource Monitoring")

        # Group agents by status
        active_agents = []
        scaffold_agents = []
        offline_agents = []

        for agent in agent_data:
            details = parse_details(agent.get('details', {}))
            status = details.get('status', agent.get('status', 'unknown'))
            mode = details.get('mode', '')

            agent_info = {
                'name': agent.get('agent', 'Unknown'),
                'status': status,
                'mode': mode,
                'last_heartbeat': agent.get('last_heartbeat', 'N/A'),
                'queue': agent.get('queue', 0),
                'cpu_percent': details.get('cpu_percent'),
                'ram_percent': details.get('ram_percent'),
                'ram_mb': details.get('ram_mb'),
                'version': details.get('version', 'N/A'),
                'details': details
            }

            if mode == 'scaffold':
                scaffold_agents.append(agent_info)
            elif status in ['healthy', 'active', 'READY']:
                active_agents.append(agent_info)
            else:
                offline_agents.append(agent_info)

        # Render Active Agents
        if active_agents:
            st.markdown("#### 🟢 Active Agents")
            cols = st.columns(min(len(active_agents), 3))
            for idx, agent_info in enumerate(active_agents):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"**{agent_info['name']}**")
                        st.markdown(f"Status: `{agent_info['status']}`")

                        if agent_info['cpu_percent'] is not None:
                            st.markdown(
                                render_resource_bar(agent_info['cpu_percent'], "CPU"),
                                unsafe_allow_html=True
                            )
                        if agent_info['ram_percent'] is not None:
                            st.markdown(
                                render_resource_bar(agent_info['ram_percent'], "RAM"),
                                unsafe_allow_html=True
                            )
                            if agent_info['ram_mb']:
                                st.caption(f"RAM: {agent_info['ram_mb']:.0f} MB")

                        st.caption(f"Last: {agent_info['last_heartbeat']}")
                        st.markdown("---")

        # Render Scaffold Agents
        if scaffold_agents:
            st.markdown("#### 🟡 Scaffold Agents (Waiting for Implementation)")
            cols = st.columns(min(len(scaffold_agents), 4))
            for idx, agent_info in enumerate(scaffold_agents):
                with cols[idx % 4]:
                    with st.container():
                        st.markdown(f"**{agent_info['name']}**")
                        st.markdown(f"Mode: `scaffold`")

                        if agent_info['cpu_percent'] is not None:
                            st.markdown(
                                render_resource_bar(agent_info['cpu_percent'], "CPU"),
                                unsafe_allow_html=True
                            )
                        if agent_info['ram_percent'] is not None:
                            st.markdown(
                                render_resource_bar(agent_info['ram_percent'], "RAM"),
                                unsafe_allow_html=True
                            )

                        st.caption(f"v{agent_info['version']}")
                        st.markdown("---")

        # Render Offline Agents
        if offline_agents:
            st.markdown("#### 🔴 Offline/Seeded Agents")
            offline_names = [a['name'] for a in offline_agents]
            st.markdown(", ".join([f"`{name}`" for name in offline_names]))

        # Summary metrics
        st.markdown("---")
        st.markdown("### 📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Agents", len(agent_data))
        with col2:
            st.metric("Active", len(active_agents))
        with col3:
            st.metric("Scaffold", len(scaffold_agents))
        with col4:
            st.metric("Offline", len(offline_agents))

        # Detailed table view
        with st.expander("📋 Detailed Agent Table"):
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

st.subheader("💻 System Health")
st.info("System-wide resource metrics aggregated from all agents are displayed above in the agent cards.")
