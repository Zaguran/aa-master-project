import streamlit as st
from datetime import datetime
from components import layout, auth, session

APP_VERSION = "1.3.9"

st.set_page_config(
    page_title=f"App",
    page_icon="🏠",
    layout="wide"
)

session.init_session_state()

build_date = datetime.now().strftime("%Y-%m-%d")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**v{APP_VERSION} | Ollama Mod: v0.5.**")
st.sidebar.markdown(f"*[cite: {build_date}]*")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Session Info")

user = auth.get_current_user()

if not auth.is_authenticated():
    st.sidebar.markdown("**Status:** Not Authenticated ❌")
    if 'last_login_error' in st.session_state and st.session_state.last_login_error:
        st.sidebar.markdown(f"**Last Login:** Failed ❌")
    
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()
else:
    st.sidebar.markdown("**Status:** Logged In ✅")
    st.sidebar.markdown(f"**Email:** {user['email']}")
    st.sidebar.markdown(f"**Roles:** {', '.join(user.get('roles', []))}")
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
