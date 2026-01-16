import streamlit as st
from components import layout, auth, session

APP_VERSION = "1.3.6"

st.set_page_config(
    page_title=f"AAT Automotive Assistance Tool v{APP_VERSION}",
    page_icon="🚗",
    layout="wide"
)

session.init_session_state()

if not auth.is_authenticated():
    st.sidebar.page_link("pages/00_Login.py", label="🔐 Login", icon="🔐")
    st.warning("Please login to access the application.")
    if st.button("Go to Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

user = auth.get_current_user()
user_roles = user.get('roles', [])
is_admin = 'admin' in user_roles

st.sidebar.page_link("pages/01_Dashboard.py", label="📊 Dashboard", icon="📊")
st.sidebar.page_link("pages/02_Status.py", label="🔄 Status", icon="🔄")
st.sidebar.page_link("pages/05_Matching.py", label="🔗 Matching", icon="🔗")
st.sidebar.page_link("pages/06_Trace.py", label="🔍 Trace", icon="🔍")

if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Admin Only**")
    st.sidebar.page_link("pages/03_DB_Status.py", label="🗄️ DB Status", icon="🗄️")
    st.sidebar.page_link("pages/04_TableView.py", label="📋 TableView", icon="📋")
    st.sidebar.page_link("pages/07_Impact.py", label="💥 Impact", icon="💥")
    st.sidebar.page_link("pages/08_Reports.py", label="📄 Reports", icon="📄")
    st.sidebar.page_link("pages/09_Chat.py", label="💬 Chat", icon="💬")
    st.sidebar.page_link("pages/99_Admin.py", label="⚙️ Admin Panel", icon="⚙️")

st.sidebar.markdown("---")


def load_css():
    """Load custom CSS from static folder."""
    try:
        with open("static/css/app.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css()

layout.render_header(f"AAT Automotive Assistance Tool v{APP_VERSION}")
layout.render_user_info()

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
