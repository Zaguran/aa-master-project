"""
Traceability Visualization Page
Version: 1.66
Task: H.2 - Interactive trace visualization UI
Displays traceability chains across V-Model
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components import auth, session, layout
from components.traceability import get_trace, generate_svg, read_svg_content

st.set_page_config(
    page_title="Traceability",
    page_icon="🔗",
    layout="wide"
)

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

# RBAC: Admin and Visitor can view
auth.require_role(["admin", "visitor"])

layout.render_header("Traceability Visualization")
st.title("🔗 Traceability View")

st.markdown("---")

# Instructions
with st.expander("ℹ️ How to use", expanded=False):
    st.markdown("""
    **Traceability Visualization** shows the complete chain of connections across the V-Model:

    - Customer Requirements → Platform Requirements
    - Platform → System → Architecture → Code
    - Code → Tests → Test Results

    **To generate a trace:**
    1. Enter the **Customer Requirement ID** (e.g., 'CR-001')
    2. Enter the **Platform Requirement ID** (e.g., 'REQ-PLAT-001')
    3. Click **Generate Trace**
    4. View the interactive graph and statistics

    **Color coding:**
    - 🔵 Customer Requirements (blue)
    - 🟠 Platform Requirements (orange)
    - 🟢 System Requirements (green)
    - 🔷 System Architecture (teal)
    - 🟣 Software Requirements (purple)
    - 🌸 Software Architecture (pink)
    - 🟡 Code Elements (yellow)
    - 🔴 Tests (red/pink)
    - 🟢 Test Results (light green)
    """)

st.markdown("---")

# Input section
col1, col2 = st.columns(2)

with col1:
    customer_req_id = st.text_input(
        "Customer Requirement ID*",
        placeholder="e.g., CR-001",
        help="Enter the customer requirement identifier (from attributes.req_id)"
    )

with col2:
    platform_req_id = st.text_input(
        "Platform Requirement ID*",
        placeholder="e.g., REQ-PLAT-001",
        help="Enter the platform requirement identifier (from attributes.req_id)"
    )

# Generate button
if st.button("🔍 Generate Trace", type="primary", use_container_width=True):
    if not customer_req_id or not platform_req_id:
        st.error("❌ Please provide both Customer Requirement ID and Platform Requirement ID")
    else:
        with st.spinner(f"Building traceability chain for {customer_req_id} → {platform_req_id}..."):
            try:
                # Get trace data
                trace = get_trace(customer_req_id, platform_req_id)

                # Check for errors
                if isinstance(trace, dict) and "error" in trace:
                    st.error(f"❌ {trace['error']}")
                    st.stop()

                # Store in session state
                st.session_state.current_trace = trace
                st.session_state.trace_customer_req_id = customer_req_id
                st.session_state.trace_platform_req_id = platform_req_id

                st.success(f"✅ Trace generated successfully!")

            except Exception as e:
                st.error(f"❌ Error generating trace: {str(e)}")
                with st.expander("Error Details"):
                    st.code(str(e))

st.markdown("---")


def get_trace_summary(trace: dict) -> dict:
    """Compute summary statistics from trace structure."""
    total_nodes = 0
    total_links = 0
    customer_requirements = 0
    tests = 0

    if trace:
        # Count nodes by category
        if trace.get('customer_req'):
            customer_requirements = 1
            total_nodes += 1
        if trace.get('platform_req'):
            total_nodes += 1

        system_nodes = trace.get('system_nodes', [])
        architecture_nodes = trace.get('architecture_nodes', [])
        code_nodes = trace.get('code_nodes', [])
        test_nodes = trace.get('test_nodes', [])

        total_nodes += len(system_nodes)
        total_nodes += len(architecture_nodes)
        total_nodes += len(code_nodes)
        total_nodes += len(test_nodes)

        tests = len(test_nodes)

        # Estimate links (each node typically has 1 incoming link except root)
        total_links = max(0, total_nodes - 1)

    return {
        'total_nodes': total_nodes,
        'total_links': total_links,
        'customer_requirements': customer_requirements,
        'tests': tests
    }


# Display trace if available
if 'current_trace' in st.session_state and st.session_state.current_trace:
    trace = st.session_state.current_trace

    # Summary statistics
    st.subheader("📊 Trace Summary")

    summary = get_trace_summary(trace)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Nodes", summary['total_nodes'])
    with col2:
        st.metric("Total Links", summary['total_links'])
    with col3:
        st.metric("Customer Reqs", summary['customer_requirements'])
    with col4:
        st.metric("Tests", summary['tests'])

    st.markdown("---")

    # Generate and display graph
    st.subheader("🔗 Traceability Graph")

    with st.spinner("Generating visualization..."):
        try:
            # Generate SVG
            output_path = "/tmp/trace_visualization"
            svg_result = generate_svg(trace, output_path, "GRAY")

            # Check if it's an error message
            if svg_result.startswith("Error:"):
                st.warning(f"⚠️ {svg_result}")
                st.info("""
                **Graphviz is required for visualization.**

                Install on Linux:
                ```
                sudo apt-get install graphviz
                ```

                Install on macOS:
                ```
                brew install graphviz
                ```
                """)
            elif os.path.exists(svg_result):
                # Read and display SVG
                svg_content = read_svg_content(svg_result)
                if svg_content:
                    st.components.v1.html(svg_content, height=800, scrolling=True)

                    # Download button
                    st.download_button(
                        label="⬇️ Download Graph (SVG)",
                        data=svg_content,
                        file_name=f"trace_{st.session_state.trace_customer_req_id}_{st.session_state.trace_platform_req_id}.svg",
                        mime="image/svg+xml"
                    )
                else:
                    st.warning("⚠️ Could not read generated SVG file.")
            else:
                st.warning(f"⚠️ SVG file not found at: {svg_result}")

        except Exception as e:
            st.error(f"❌ Error generating visualization: {str(e)}")
            with st.expander("Error Details"):
                st.code(str(e))

    st.markdown("---")

    # Detailed breakdown
    with st.expander("📋 Detailed Node Breakdown", expanded=False):
        st.markdown("### Nodes by Category")

        # Customer requirement
        customer_req = trace.get('customer_req')
        if customer_req:
            st.markdown("**🔵 Customer Requirement:** 1 node")
            with st.expander("Show Customer Requirement"):
                st.markdown(f"- **{customer_req.get('node_id', 'N/A')}**: {str(customer_req.get('text', 'N/A'))[:100]}...")

        # Platform requirement
        platform_req = trace.get('platform_req')
        if platform_req:
            st.markdown("**🟠 Platform Requirement:** 1 node")
            with st.expander("Show Platform Requirement"):
                st.markdown(f"- **{platform_req.get('node_id', 'N/A')}**: {str(platform_req.get('text', 'N/A'))[:100]}...")

        # System nodes
        system_nodes = trace.get('system_nodes', [])
        if system_nodes:
            st.markdown(f"**🟢 System Nodes:** {len(system_nodes)} node(s)")
            with st.expander("Show System Nodes"):
                for node in system_nodes:
                    st.markdown(f"- **{node.get('node_id', 'N/A')}**: {str(node.get('text', 'N/A'))[:100]}...")

        # Architecture nodes
        architecture_nodes = trace.get('architecture_nodes', [])
        if architecture_nodes:
            st.markdown(f"**🔷 Architecture Nodes:** {len(architecture_nodes)} node(s)")
            with st.expander("Show Architecture Nodes"):
                for node in architecture_nodes:
                    st.markdown(f"- **{node.get('node_id', 'N/A')}**: {str(node.get('text', 'N/A'))[:100]}...")

        # Code nodes
        code_nodes = trace.get('code_nodes', [])
        if code_nodes:
            st.markdown(f"**🟡 Code Elements:** {len(code_nodes)} node(s)")
            with st.expander("Show Code Elements"):
                for node in code_nodes:
                    st.markdown(f"- **{node.get('node_id', 'N/A')}**: {str(node.get('text', 'N/A'))[:100]}...")

        # Test nodes
        test_nodes = trace.get('test_nodes', [])
        if test_nodes:
            st.markdown(f"**🔴 Test Nodes:** {len(test_nodes)} node(s)")
            with st.expander("Show Test Nodes"):
                for node in test_nodes:
                    st.markdown(f"- **{node.get('node_id', 'N/A')}**: {str(node.get('text', 'N/A'))[:100]}...")

else:
    st.info("👆 Enter a Customer Requirement ID and Platform Requirement ID above to generate a traceability chain")

    # Example usage
    st.markdown("---")
    st.markdown("### 💡 Example")
    st.code("""
Customer Requirement ID: CR-001
Platform Requirement ID: REQ-PLAT-001
    """)
    st.markdown("This will show the complete traceability from customer requirement CR-001 through the platform requirement REQ-PLAT-001 and down through the entire V-Model.")
