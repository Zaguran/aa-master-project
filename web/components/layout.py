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
        
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            auth.logout()
            st.switch_page("app.py")
