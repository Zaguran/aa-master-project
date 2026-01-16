import streamlit as st
from components import auth


def render_header(title: str):
    """Render application header with custom styling."""
    st.markdown(
        f'<div class="header">{title}</div>',
        unsafe_allow_html=True
    )


def render_user_info():
    """Render user information and logout button in sidebar."""
    user = auth.get_current_user()
    
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Info")
        st.sidebar.markdown(f"**Email:** {user['email']}")
        st.sidebar.markdown(f"**Name:** {user.get('full_name', 'N/A')}")
        st.sidebar.markdown(f"**Roles:** {', '.join(user.get('roles', []))}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            auth.logout()
            st.rerun()
