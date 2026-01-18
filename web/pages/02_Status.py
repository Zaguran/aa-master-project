"""
System Status Page with Live Agent Monitoring
Version: 1.8
"""

import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components import auth, session, layout, agents
from agents.db_bridge.database import get_connection, list_agent_status
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Status", page_icon="📊", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin", "visitor"])

layout.render_header("System Status")
st.title("📊 System Status")

# Auto-refresh state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh"):
        st.session_state.last_refresh = time.time()
        st.rerun()

st.markdown("---")

# Agent Status
st.subheader("🤖 Agent Status")

try:
    agent_data = list_agent_status()

    if agent_data:
        # Create metrics row
        num_agents = len(agent_data)
        cols = st.columns(min(num_agents, 6))

        for i, agent in enumerate(agent_data[:6]):
            with cols[i]:
                # Status indicator
                status = agent.get('status', 'UNKNOWN')
                details = agent.get('details', {})
                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except:
                        details = {}

                # Check mode for scaffold agents
                mode = details.get('mode', '')

                if mode == 'scaffold':
                    status_color = '🟡'
                    status = 'SCAFFOLD'
                elif status == 'ACTIVE' or status == 'READY':
                    status_color = '🟢'
                else:
                    status_color = '🔴'

                # Last heartbeat
                last_hb = agent.get('last_heartbeat')
                if last_hb:
                    if last_hb.tzinfo:
                        now = datetime.now(last_hb.tzinfo)
                    else:
                        now = datetime.now()
                    time_diff = now - last_hb
                    if time_diff < timedelta(minutes=5):
                        hb_status = '✅'
                    else:
                        hb_status = '⚠️'
                    hb_seconds = time_diff.total_seconds()
                else:
                    hb_status = '❌'
                    hb_seconds = None

                # Display
                agent_name = agent['agent_name'].replace('_', ' ').title()
                if len(agent_name) > 12:
                    agent_name = agent_name[:12] + '...'

                st.metric(
                    label=f"{status_color} {agent_name}",
                    value=status,
                    delta=f"Q: {agent.get('queue_size', 0)}"
                )

                if hb_seconds is not None:
                    if hb_seconds < 60:
                        st.caption(f"{hb_status} {hb_seconds:.0f}s ago")
                    elif hb_seconds < 3600:
                        st.caption(f"{hb_status} {hb_seconds/60:.0f}m ago")
                    else:
                        st.caption(f"{hb_status} {hb_seconds/3600:.1f}h ago")
                else:
                    st.caption("❌ Never")

        st.markdown("---")

        # Detailed agent table
        st.subheader("📋 Detailed Agent Information")

        agent_table_data = []
        for agent in agent_data:
            last_hb = agent.get('last_heartbeat')
            if last_hb:
                if last_hb.tzinfo:
                    now = datetime.now(last_hb.tzinfo)
                else:
                    now = datetime.now()
                time_since = (now - last_hb).total_seconds()
                if time_since < 60:
                    hb_str = f"{time_since:.0f}s ago"
                elif time_since < 3600:
                    hb_str = f"{time_since/60:.0f}m ago"
                else:
                    hb_str = f"{time_since/3600:.1f}h ago"
            else:
                hb_str = "Never"

            details = agent.get('details', {})
            if isinstance(details, str):
                try:
                    details = json.loads(details)
                except:
                    details = {}

            agent_table_data.append({
                'Agent': agent['agent_name'],
                'Status': agent.get('status', 'UNKNOWN'),
                'Queue Size': agent.get('queue_size', 0),
                'Last Heartbeat': hb_str,
                'Mode': details.get('mode', 'N/A'),
                'RAM (MB)': details.get('ram_mb', 'N/A'),
                'CPU %': details.get('cpu_percent', 'N/A')
            })

        df = pd.DataFrame(agent_table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Queue visualization
        st.subheader("📊 Queue Status")

        queue_data = []
        for agent in agent_data:
            queue_size = agent.get('queue_size', 0)
            if queue_size > 0:
                queue_data.append({
                    'Agent': agent['agent_name'],
                    'Queue': queue_size
                })

        if queue_data:
            try:
                import plotly.express as px
                df_queue = pd.DataFrame(queue_data)
                fig = px.bar(df_queue, x='Agent', y='Queue',
                             title='Agent Queue Sizes',
                             color='Queue',
                             color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.warning("Plotly not available for charts")
                st.dataframe(pd.DataFrame(queue_data), use_container_width=True, hide_index=True)
        else:
            st.info("✅ All queues empty")

    else:
        st.warning("No agent status available")

except Exception as e:
    st.error("⚠️ Unable to retrieve agent status. Database or agents may be offline.")
    st.info("This is normal if agents are starting up or running on a different server.")
    with st.expander("Error Details"):
        st.code(str(e))

st.markdown("---")

# Database Status
st.subheader("💾 Database Status")

try:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Table sizes
    cur.execute("""
        SELECT
            tablename,
            pg_size_pretty(pg_total_relation_size('work_aa.' || tablename)) AS size
        FROM pg_tables
        WHERE schemaname = 'work_aa'
        ORDER BY pg_total_relation_size('work_aa.' || tablename) DESC
        LIMIT 10
    """)

    tables = cur.fetchall()

    if tables:
        table_data = []
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) as count FROM work_aa.{table['tablename']}")
                count = cur.fetchone()['count']
            except:
                count = 'N/A'

            table_data.append({
                'Table': table['tablename'],
                'Rows': count,
                'Size': table['size']
            })

        df_tables = pd.DataFrame(table_data)
        st.dataframe(df_tables, use_container_width=True, hide_index=True)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Error loading database status: {e}")

# Auto-refresh timer
st.markdown("---")
st.caption(f"Last refresh: {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%H:%M:%S')}")
st.caption("Click Refresh button to update status")
