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
        st.switch_page("pages/00_Login.py")
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
        st.switch_page("pages/99_Admin.py")
    st.stop()

platform_options = {p['name']: p['platform_id'] for p in platforms}
selected_platform = st.selectbox(
    "Select Platform*",
    options=list(platform_options.keys()),
    help="Choose which platform to import data for"
)

platform_id = platform_options[selected_platform]

# ============================================================================
# DROPDOWN 2: SELECT DATA TYPE
# ============================================================================
data_types = {
    "Platform Requirements": "platform_requirements",
    "System Requirements": "system_requirements",
    "Architecture Elements": "architecture_elements",
    "Code Elements": "code_elements",
    "Test Cases": "test_cases",
    "Test Results": "test_results",
    "Traceability Links": "links"
}

selected_data_type_label = st.selectbox(
    "Data Type*",
    options=list(data_types.keys()),
    help="Select the type of data you are importing"
)

data_type = data_types[selected_data_type_label]

# Show implementation status
if data_type != "platform_requirements":
    st.info(f"Note: '{selected_data_type_label}' import is planned for future implementation. Currently only 'Platform Requirements' is fully supported.")

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
- Platform: **{selected_platform}** (`{platform_id}`)
- Data Type: **{selected_data_type_label}**

**Supported File Formats:** CSV, JSONL
""")

# Show format details based on selected data type
with st.expander("CSV/JSONL Format Reference"):
    if data_type == "platform_requirements":
        st.markdown("""
        **Platform Requirements Format:**
        ```
        req_id, text, type, priority, asil, owner, version, baseline, status
        ```

        Example:
        ```csv
        req_id,text,type,priority,asil,owner,version,baseline,status
        PLAT-001,The system shall support 100 concurrent users,functional,high,QM,Team A,1.0,B1,approved
        PLAT-002,Response time shall be under 200ms,performance,medium,ASIL-B,Team B,1.0,B1,draft
        ```
        """)
    elif data_type == "system_requirements":
        st.markdown("""
        **System Requirements Format:** *(Coming Soon)*
        ```
        req_id, text, parent_req, subsystem, verification_method, ...
        ```
        """)
    elif data_type == "architecture_elements":
        st.markdown("""
        **Architecture Elements Format:** *(Coming Soon)*
        ```
        arch_id, name, type, diagram_path, description, ...
        ```
        """)
    elif data_type == "code_elements":
        st.markdown("""
        **Code Elements Format:** *(Coming Soon)*
        ```
        code_id, file_path, function_name, lines_of_code, complexity, ...
        ```
        """)
    elif data_type == "test_cases":
        st.markdown("""
        **Test Cases Format:** *(Coming Soon)*
        ```
        test_id, name, type, description, expected_result, ...
        ```
        """)
    elif data_type == "test_results":
        st.markdown("""
        **Test Results Format:** *(Coming Soon)*
        ```
        result_id, test_id, status, execution_date, ...
        ```
        """)
    elif data_type == "links":
        st.markdown("""
        **Traceability Links Format:** *(Coming Soon)*
        ```
        source_id, source_type, target_id, target_type, link_type
        ```
        """)

st.markdown("---")
st.caption("Refer to project documentation for detailed format specifications.")
