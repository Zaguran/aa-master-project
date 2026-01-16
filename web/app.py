import sys
import os
# Přidání kořenového adresáře do PYTHONPATH pro Docker
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("/app")

import streamlit as st
from datetime import datetime
from components import layout, auth, session
from agents.db_bridge.database import list_agent_status

APP_VERSION = "1.4.5.8"

# Startup logging for Docker debugging
db_host = os.getenv('DB_HOST', 'LINUX_1_IP')
print(f"[AAT Web v{APP_VERSION}] Starting up...")
print(f"[AAT Web v{APP_VERSION}] Connecting to DB at {db_host}...")
print(f"[AAT Web v{APP_VERSION}] PYTHONPATH: {os.getenv('PYTHONPATH', 'not set')}")

st.set_page_config(
    page_title=f"🏠 App Home",
    page_icon="🏠",
    layout="wide"
)

session.init_session_state()

build_date = "2026-01-11"

# Error resilience: Wrap DB-dependent operations to prevent 502 errors
db_available = True
user = None
try:
    user = auth.get_current_user()
except Exception as e:
    db_available = False
    print(f"[AAT Web] ERROR: Database connection failed: {e}")
    print(f"[AAT Web] Container will continue running, showing error to user...")
    user = None

# Get Ollama status from DB (reads from work_aa.agent_status via LINUX_1_IP)
ollama_status = "v0.5 | Mode: unknown"
try:
    agents = list_agent_status()
    for agent in agents:
        if agent['agent_name'] == 'monitor_ollama_server':
            details = agent.get('details', {})
            if isinstance(details, dict):
                version = details.get('module_version', 'v0.5')
                mode = details.get('mode', 'unknown')
                ollama_status = f"{version} | Mode: {mode}"
            break
except Exception as e:
    print(f"[AAT Web] Warning: Could not read Ollama status from DB: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**v{APP_VERSION} | Ollama Mod: {ollama_status}**")
st.sidebar.markdown(f"*[cite: {build_date}]*")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Session Info")

# Show DB status warning if unavailable
if not db_available:
    st.sidebar.error("⚠️ Database on Linux 1 is temporarily unavailable")
    st.sidebar.info("Please wait while connection is restored...")

if not db_available or not auth.is_authenticated():
    st.sidebar.markdown("**Status:** Not Authenticated ❌")
    if 'last_login_error' in st.session_state and st.session_state.last_login_error:
        st.sidebar.markdown(f"**Last Login:** Failed ❌")
    
    # Check if session was revoked
    if st.session_state.get('session_id'):
        from components import session as sess
        if not sess.validate_session(st.session_state.session_id):
            st.sidebar.markdown("**Status:** Session Revoked ⚠️")
    
    if not db_available:
        st.error("🔌 Database Connection Error")
        st.warning("**Databáze na Linuxu 1 je dočasně nedostupná**")
        st.info("The application is running, but cannot connect to the database. Please check:")
        st.code(f"DB_HOST: {os.getenv('DB_HOST', 'not set')}\nDB_PORT: {os.getenv('DB_PORT', 'not set')}\nDB_NAME: {os.getenv('DB_NAME', 'not set')}")
        st.markdown("Contact your administrator if this issue persists.")
        st.stop()
    else:
        st.warning("Please login to access the application.")
        if st.button("Goto Login Page", type="primary"):
            st.switch_page("pages/00_Login.py")
        st.stop()
else:
    user_roles = user.get('roles', [])
    primary_role = user_roles[0] if user_roles else 'user'
    st.sidebar.markdown(f"**Status:** {user['full_name']} ({primary_role}) ✅")
    st.sidebar.markdown(f"**Email:** {user['email']}")
    if len(user_roles) > 1:
        st.sidebar.markdown(f"**All Roles:** {', '.join(user_roles)}")
    if 'last_login_success' in st.session_state and st.session_state.last_login_success:
        st.sidebar.markdown("**Last Login:** Success ✅")


def load_css():
    """Load custom CSS from static folder."""
    try:
        with open("static/css/app.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css()

layout.render_header(f"App v{APP_VERSION}")

if st.session_state.get('logout_message'):
    st.success(st.session_state.logout_message)
    del st.session_state.logout_message

st.markdown("---")
st.success(f"Welcome, {user['full_name']}!")
st.info("Use the navigation menu on the left to access different modules.")
st.markdown("---")

st.markdown("### Available Modules")

modules = [
    ("Dashboard", "System overview and key metrics"),
    ("Status", "Agent and system status monitoring"),
    ("DB Status", "Database health and statistics"),
    ("TableView", "Browse database tables"),
    ("Matching", "Requirements matching interface"),
    ("Trace", "Traceability analysis"),
    ("Impact", "Git impact analysis"),
    ("Reports", "Generate and view reports"),
    ("Chat", "AI chat interface (Type A)")
]

if auth.has_role("admin"):
    modules.append(("Admin Panel", "System administration (Admin only)"))

for name, desc in modules:
    st.markdown(f"- **{name}** - {desc}")
