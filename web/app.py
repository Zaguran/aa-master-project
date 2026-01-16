import streamlit as st
from components import layout, auth, session

APP_VERSION = "1.3.5"

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

user = auth.get_current_user()

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
