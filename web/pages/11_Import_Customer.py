import streamlit as st
from components import auth, session, layout
from components import importer

st.set_page_config(page_title="Import Customer", page_icon="📥", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/99_Login_Logout.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Import Customer Requirements")
st.title("📥 Import Customer Requirements")

st.markdown("---")

customer_id = st.text_input(
    "Customer ID",
    value="A",
    help="Enter customer identifier (e.g., A, B, ProjectX)"
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "jsonl"],
    help="Upload customer requirements in CSV or JSONL format"
)

filetype = st.radio("File Format", ["csv", "jsonl"])

if st.button("Import Customer Requirements", type="primary"):
    if not customer_id.strip():
        st.warning("Please enter a Customer ID")
    elif uploaded_file:
        with st.spinner("Importing..."):
            try:
                result = importer.import_customer_file(
                    customer_id.strip(),
                    uploaded_file.read(),
                    filetype
                )
                if result.get("status") == "success":
                    st.success(f"Successfully imported {result['inserted']} requirements for customer '{customer_id}'!")
                    with st.expander("Import Details"):
                        st.json({
                            "customer_id": customer_id.strip(),
                            "inserted": result.get("inserted", 0),
                            "failed": result.get("failed", 0),
                            "status": result.get("status", "")
                        })
                else:
                    st.error(f"Import failed: {result.get('status', 'Unknown error')}")
            except Exception as e:
                st.error(f"Import failed: {str(e)}")
                with st.expander("Error Details"):
                    st.code(str(e))
    else:
        st.warning("Please select a file first")

st.markdown("---")
st.markdown("### 📖 Instructions")

st.info("""
**Customer requirements** are needs from a specific customer project.

**CSV Format:**
- req_id: Requirement identifier (e.g., CR-001)
- text: Requirement description
- priority: Priority level (HIGH, MEDIUM, LOW)
- source_doc: Source document reference
- category: Category/domain (optional)
- **id_type**: 'requirement' (default) or 'information'

**JSONL Format:**
One JSON object per line with the same fields.

**Note on id_type:**
- 'requirement': Standard requirement (used for matching)
- 'information': Supporting information (not matched)

Example files are available in the project documentation.
""")
