import streamlit as st
from components import auth, session

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

session.init_session_state()

if not auth.is_authenticated():
    st.switch_page("pages/00_Login.py")

auth.require_role(["admin"])

st.title("⚙️ Admin Panel")
st.markdown("---")

user = auth.get_current_user()

st.success(f"Welcome, {user['full_name']} ({user['email']})")

st.markdown("### Admin Functions")
st.info("Admin panel features will be implemented in future versions.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### User Management")
    st.markdown("- View all users")
    st.markdown("- Create new users")
    st.markdown("- Manage roles")
    st.markdown("- Deactivate users")

with col2:
    st.markdown("#### System Settings")
    st.markdown("- Configure system parameters")
    st.markdown("- Manage database connections")
    st.markdown("- View system logs")
    st.markdown("- Monitor agent status")

st.markdown("---")
st.markdown("**Note:** This is a placeholder page. Full admin functionality will be added in future releases.")
