import streamlit as st
from components import layout

APP_VERSION = "1.1.0"

st.set_page_config(
    page_title=f"AAT Automotive Assistance Tool v{APP_VERSION}",
    page_icon="🚗",
    layout="wide"
)


def load_css():
    """Load custom CSS from static folder."""
    try:
        with open("static/css/app.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css()

layout.render_header(f"AAT Automotive Assistance Tool v{APP_VERSION}")

st.markdown("---")
st.info("Welcome to the AAT system. Use the navigation menu on the left to access different modules.")
st.markdown("---")

st.markdown("### Available Modules")
st.markdown("""
- **Dashboard** - System overview and key metrics
- **Status** - Agent and system status monitoring
- **DB Status** - Database health and statistics
- **TableView** - Browse database tables
- **Matching** - Requirements matching interface
- **Trace** - Traceability analysis
- **Impact** - Git impact analysis
- **Reports** - Generate and view reports
- **Chat** - AI chat interface (Type A)
""")
