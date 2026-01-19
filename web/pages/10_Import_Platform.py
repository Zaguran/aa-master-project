import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")

from components import auth, session, layout
from components import importer
from agents.db_bridge import database

st.set_page_config(page_title="Import Platform", page_icon="📥", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/99_Login_Logout.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Import Platform Data")
st.title("📥 Import Platform Data")

st.markdown("---")

# ============================================================================
# DROPDOWN 1: SELECT PLATFORM
# ============================================================================
try:
    platforms = database.list_platforms()
except Exception as e:
    st.error(f"Error loading platforms: {e}")
    platforms = []

if not platforms:
    st.warning("No platforms found. Please create a platform in Admin panel first.")
    if st.button("Go to Admin Panel", type="primary"):
        st.switch_page("pages/98_Admin.py")
    st.stop()

platform_options = {p['name']: p['platform_id'] for p in platforms}
selected_platform = st.selectbox(
    "Select Platform*",
    options=list(platform_options.keys()),
    help="Choose which platform to import data for"
)

platform_id = platform_options[selected_platform]

# ============================================================================
# DROPDOWN 2: SELECT DATA TYPE (aligned with V-Model)
# ============================================================================
data_types = {
    # LEFT SIDE - Requirements & Architecture
    "System Requirements": "system_requirements",
    "System Architecture": "system_architecture",
    "Software Requirements": "software_requirements",
    "Software Architecture": "software_architecture",

    # RIGHT SIDE - Testing
    "System Test": "system_test",
    "System Integration Test": "system_integration_test",
    "Software Test": "software_test",
    "Software Integration Test": "software_integration_test",

    # TEST RESULTS
    "System Test Result": "system_test_result",
    "System Integration Test Result": "system_integration_test_result",
    "Software Test Result": "software_test_result",
    "Software Integration Test Result": "software_integration_test_result",

    # TRACEABILITY
    "Traceability Links": "traceability_links"
}

selected_data_type_label = st.selectbox(
    "Data Type*",
    options=list(data_types.keys()),
    help="Select the type of data you are importing"
)

data_type = data_types[selected_data_type_label]

# Show implementation status
st.info(f"Note: Import functionality is being implemented. Currently preparing data structure for '{selected_data_type_label}'.")

st.markdown("---")

# ============================================================================
# FILE UPLOADER
# ============================================================================
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "jsonl"],
    help="Upload data file in CSV or JSONL format"
)

filetype = st.radio("File Format", ["csv", "jsonl"], horizontal=True)

# ============================================================================
# IMPORT BUTTON
# ============================================================================
if st.button("Import Data", type="primary"):
    if uploaded_file:
        with st.spinner(f"Importing {selected_data_type_label} for {selected_platform}..."):
            try:
                result = importer.import_platform_file(
                    uploaded_file.read(),
                    filetype,
                    platform_id=platform_id,
                    data_type=data_type
                )
                if result.get("status") == "success":
                    st.success(f"Successfully imported {result.get('inserted', 0)} items!")
                    with st.expander("Import Details"):
                        st.json({
                            "platform": selected_platform,
                            "platform_id": platform_id,
                            "data_type": selected_data_type_label,
                            "inserted": result.get("inserted", 0),
                            "failed": result.get("failed", 0)
                        })
                else:
                    st.warning(f"Import result: {result.get('status', 'Unknown')}")
                    with st.expander("Details"):
                        st.json(result)
            except Exception as e:
                st.error(f"Import failed: {str(e)}")
                with st.expander("Error Details"):
                    st.code(str(e))
    else:
        st.warning("Please select a file first")

# ============================================================================
# INSTRUCTIONS
# ============================================================================
st.markdown("---")
st.markdown("### 📖 Instructions")

st.info(f"""
**Current Selection:**
- Platform: {selected_platform}
- Data Type: {selected_data_type_label}

**V-Model Structure:**

Left Side (Requirements & Architecture):
• System Requirements → System Architecture
• Software Requirements → Software Architecture

Right Side (Testing):
• System Test → System Integration Test
• Software Test → Software Integration Test

Results:
• System Test Result, System Integration Test Result
• Software Test Result, Software Integration Test Result

Traceability:
• Links between all layers (source_id, source_type, target_id, target_type, link_type)

**CSV Format includes:**
- **id_type** column: 'requirement' (default) or 'information'
  - requirement: Standard requirement nodes
  - information: Supporting information nodes
- Other columns vary by data type (see documentation)
""")

# Show format details based on selected data type
with st.expander("CSV/JSONL Format Reference"):
    if data_type in ["system_requirements", "software_requirements"]:
        st.markdown(f"""
        **{selected_data_type_label} Format:**
        ```
        req_id, text, type, priority, asil, owner, version, baseline, status
        ```

        Example:
        ```csv
        req_id,text,type,priority,asil,owner,version,baseline,status
        SYS-001,The system shall support 100 concurrent users,functional,high,QM,Team A,1.0,B1,approved
        SYS-002,Response time shall be under 200ms,performance,medium,ASIL-B,Team B,1.0,B1,draft
        ```
        """)
    elif data_type in ["system_architecture", "software_architecture"]:
        st.markdown(f"""
        **{selected_data_type_label} Format:**
        ```
        arch_id, name, type, parent_id, description, diagram_ref
        ```

        Example:
        ```csv
        arch_id,name,type,parent_id,description,diagram_ref
        ARCH-001,Main Controller,component,,Central processing unit,diagrams/main.png
        ARCH-002,Sensor Module,component,ARCH-001,Input sensor handling,diagrams/sensor.png
        ```
        """)
    elif data_type in ["system_test", "system_integration_test", "software_test", "software_integration_test"]:
        st.markdown(f"""
        **{selected_data_type_label} Format:**
        ```
        test_id, name, type, description, preconditions, expected_result, linked_req
        ```

        Example:
        ```csv
        test_id,name,type,description,preconditions,expected_result,linked_req
        TST-001,User Login Test,functional,Verify user can login,System running,Login successful,SYS-001
        TST-002,Performance Test,performance,Verify response time,System under load,<200ms,SYS-002
        ```
        """)
    elif data_type in ["system_test_result", "system_integration_test_result", "software_test_result", "software_integration_test_result"]:
        st.markdown(f"""
        **{selected_data_type_label} Format:**
        ```
        result_id, test_id, status, execution_date, tester, notes
        ```

        Example:
        ```csv
        result_id,test_id,status,execution_date,tester,notes
        RES-001,TST-001,PASSED,2026-01-17,John Doe,All checks passed
        RES-002,TST-002,FAILED,2026-01-17,Jane Smith,Response time 250ms
        ```
        """)
    elif data_type == "traceability_links":
        st.markdown("""
        **Traceability Links Format:**
        ```
        source_id, source_type, target_id, target_type, link_type
        ```

        Example:
        ```csv
        source_id,source_type,target_id,target_type,link_type
        SYS-001,system_requirements,ARCH-001,system_architecture,derives
        ARCH-001,system_architecture,TST-001,system_test,verified_by
        TST-001,system_test,RES-001,system_test_result,has_result
        ```
        """)

st.markdown("---")
st.caption("Refer to project documentation for detailed format specifications.")
