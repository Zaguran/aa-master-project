"""
Matching Page with G.2 Matching Engine UI
Version: 1.8.1
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components import auth, session, layout
from components.matching import run_matching, get_coverage_summary
from agents.db_bridge.database import list_projects

st.set_page_config(page_title="Matching", page_icon="🔗", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin", "visitor"])

layout.render_header("Requirements Matching")
st.title("🔗 Requirements Matching")

st.markdown("---")

# Instructions
with st.expander("ℹ️ About Matching", expanded=False):
    st.markdown("""
    **Matching Engine** compares customer requirements to platform requirements using AI-powered similarity analysis.

    **How it works:**
    1. Embeddings must be generated first (see Embeddings page)
    2. Cosine similarity is calculated between customer and platform requirement vectors
    3. Top-K matches are stored for each customer requirement
    4. Coverage classification is applied based on thresholds

    **Classification:**
    - 🟢 **GREEN** (≥0.85): Full match - requirement is covered
    - 🟡 **YELLOW** (≥0.65): Partial match - needs review
    - 🔴 **RED** (<0.65): No match - gap identified
    """)

st.markdown("---")
st.subheader("📋 Select Projects to Match")

# Get projects
try:
    all_projects = list_projects()

    customer_projects = [p['project_id'] for p in all_projects if p.get('type') == 'CUSTOMER']
    platform_projects = [p['project_id'] for p in all_projects if p.get('type') == 'PLATFORM']

    col1, col2 = st.columns(2)

    with col1:
        if customer_projects:
            selected_customer = st.selectbox(
                "Customer Project*",
                options=customer_projects,
                help="Select customer project to match"
            )
        else:
            st.warning("No customer projects found. Please import customer data first.")
            selected_customer = None

    with col2:
        if platform_projects:
            selected_platform = st.selectbox(
                "Platform Project*",
                options=platform_projects,
                help="Select platform to match against"
            )
        else:
            st.warning("No platform projects found. Please import platform data first.")
            selected_platform = None

except Exception as e:
    st.error(f"Error loading projects: {e}")
    selected_customer = None
    selected_platform = None

st.markdown("---")
st.subheader("🎯 Run Matching Engine")

st.markdown("""
Match customer requirements to platform requirements using AI-powered similarity analysis.
""")

# Configuration
col1, col2, col3 = st.columns(3)

with col1:
    top_k = st.slider("Top K Matches", min_value=1, max_value=10, value=5,
                     help="Number of best matches per customer requirement")

with col2:
    green_threshold = st.slider("GREEN Threshold", min_value=0.5, max_value=1.0, value=0.85, step=0.05,
                                help="Full match threshold")

with col3:
    yellow_threshold = st.slider("YELLOW Threshold", min_value=0.5, max_value=1.0, value=0.65, step=0.05,
                                 help="Partial match threshold")

# Only enable if projects are selected
matching_enabled = selected_customer is not None and selected_platform is not None

# Run matching
if st.button("🚀 Run Matching", type="primary", use_container_width=True, disabled=not matching_enabled):
    if not matching_enabled:
        st.error("❌ Please select both customer and platform projects")
    else:
        with st.spinner("Running matching engine..."):
            try:
                result = run_matching(
                    model='nomic-embed-text',
                    top_k=top_k,
                    full_threshold=green_threshold,
                    partial_threshold=yellow_threshold
                )

                st.success("✅ Matching completed!")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Matches Created", result.get('matched', 0))
                with col2:
                    st.metric("Errors", result.get('errors', 0))

            except Exception as e:
                st.error(f"❌ Error running matching: {str(e)}")
                with st.expander("Error Details"):
                    st.code(str(e))

st.markdown("---")

# Coverage summary
st.subheader("📊 Coverage Summary")

try:
    summary = get_coverage_summary(model_id=1)

    if summary.get('total', 0) > 0:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Requirements", summary['total'])
        with col2:
            st.metric("🟢 GREEN (Full)", f"{summary['green']} ({summary['pct_green']}%)")
        with col3:
            st.metric("🟡 YELLOW (Partial)", f"{summary['yellow']} ({summary['pct_yellow']}%)")
        with col4:
            st.metric("🔴 RED (No Match)", f"{summary['red']} ({summary['pct_red']}%)")

        # Pie chart
        try:
            import plotly.graph_objects as go

            fig = go.Figure(data=[go.Pie(
                labels=['GREEN', 'YELLOW', 'RED'],
                values=[summary['green'], summary['yellow'], summary['red']],
                marker=dict(colors=['#4CAF50', '#FFC107', '#F44336'])
            )])

            fig.update_layout(title='Coverage Classification')
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("Plotly not available for pie chart visualization")

    else:
        st.info("No matches found yet. Run matching first!")

except Exception as e:
    st.error(f"Error loading coverage: {e}")
    with st.expander("Error Details"):
        st.code(str(e))
