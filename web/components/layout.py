import streamlit as st


def render_header(title: str):
    """Render application header with custom styling."""
    st.markdown(
        f'<div class="header">{title}</div>',
        unsafe_allow_html=True
    )
