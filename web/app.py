import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime
from components import layout, auth, session
from agents.db_bridge.database import list_agent_status

APP_VERSION = "1.8.2"

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

# Dynamic build date
build_date = datetime.now().strftime("%Y-%m-%d %H:%M")

# Check Ollama API availability for Mode status
ollama_mode = "Offline"
try:
    ollama_base = os.getenv('OLLAMA_API_BASE', os.getenv('OLLAMA_BASE_URL', ''))
    if ollama_base:
        import requests
        response = requests.get(f"{ollama_base}/api/tags", timeout=2)
        if response.status_code == 200:
            ollama_mode = "Online"
except Exception as e:
    print(f"[AAT Web] Ollama API check: {e}")
    ollama_mode = "Offline"

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

# Sidebar Build Information for v0.5
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏗️ Build Information")
st.sidebar.markdown(f"**Build:** v{APP_VERSION}")
st.sidebar.markdown(f"**Build Date:** {build_date}")
st.sidebar.markdown(f"**Ollama Module:** v0.5")
st.sidebar.markdown(f"**Mode:** {ollama_mode}")

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

st.subheader("What is AA PoC?")

st.markdown("""
**AA PoC (Automotive Acceptance Proof of Concept)** is an AI-powered platform for matching
customer requirements to platform capabilities in automotive development.

**Key Features:**
- Import requirements from customers and platforms
- Generate AI embeddings for semantic understanding
- Match customer needs to platform features
- Trace requirements through V-Model (system -> architecture -> code -> tests)
- AI chat interface for requirement analysis
""")

st.markdown("---")

st.subheader("Core Workflow")

st.markdown("""
The system follows a sequential workflow:
""")

# Workflow visualization using columns
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### 1. Import Data")
    st.info("""
**Import Platform**
- Platform requirements
- Architecture documents
- Test specifications

**Import Customer**
- Customer requirements
- RFQ documents

Both imports go into database in parallel.
Platform data must exist before matching.
""")

with col2:
    st.markdown("### 2. Process")
    st.info("""
**Generate Embeddings**
- Convert text to vectors
- Uses Ollama AI (nomic-embed-text)
- Captures semantic meaning

**Run Matching**
- Compare customer <-> platform
- Calculate similarity scores
- Classify: GREEN/YELLOW/RED
""")

with col3:
    st.markdown("### 3. Analyze")
    st.info("""
**View Trace**
- Complete V-Model chain
- Requirements -> Tests
- Visual graph display

**AI Chat**
- Ask questions
- Analyze requirements
- Get recommendations
""")

st.markdown("---")

st.markdown("### Process Flow")

# Simple text-based flow for clarity
flow_text = """
+-------------------+     +-------------------+
| Import Platform   |---->|   Database        |
+-------------------+     |                   |
                          |   PostgreSQL      |
+-------------------+     |   +               |
| Import Customer   |---->|   pgvector        |
+-------------------+     +---------+---------+
                                    |
                                    v
                          +-------------------+
                          |  Embeddings       |
                          |  (Ollama AI)      |
                          +---------+---------+
                                    |
                                    v
                          +-------------------+
                          |   Matching        |
                          |  (Similarity)     |
                          +---------+---------+
                                    |
                                    v
                          +-------------------+
                          | Trace & Chat      |
                          |  (Analysis)       |
                          +-------------------+
"""

st.code(flow_text, language="text")

st.markdown("---")

st.subheader("Getting Started")

st.markdown("""
**New users should follow this sequence:**

1. **Import Platform** - Upload platform requirements first
2. **Import Customer** - Upload customer requirements
3. **Embeddings** - Generate AI embeddings for all requirements
4. **Matching** - Run matching engine
5. **Dashboard** - View coverage statistics
6. **Trace** - Explore requirement chains
7. **Chat** - Ask AI about requirements

**For monitoring:**
- **Status** - Check agent health
- **DB Status** - View database statistics

**For administration:**
- **Admin Panel** - Manage users, projects (admin only)
""")

st.markdown("---")
