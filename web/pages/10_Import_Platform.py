import streamlit as st
from components import auth, session, layout
from components import importer

st.set_page_config(page_title="Import Platform", page_icon="📥", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/00_Login.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Import Platform Requirements")
st.title("📥 Import Platform Requirements")

st.markdown("---")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "jsonl"],
    help="Upload platform requirements in CSV or JSONL format"
)

filetype = st.radio("File Format", ["csv", "jsonl"])

if st.button("Import Platform Requirements", type="primary"):
    if uploaded_file:
        with st.spinner("Importing..."):
            try:
                result = importer.import_platform_file(
                    uploaded_file.read(),
                    filetype
                )
                if result.get("status") == "success":
                    st.success(f"Successfully imported {result['inserted']} requirements!")
                    with st.expander("Import Details"):
                        st.json({
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
st.markdown("### Instructions")
st.info("""
**Platform requirements** define the capabilities of your platform (e.g., Platform_A).

**CSV Format**: req_id, text, type, priority, asil, owner, version, baseline, status

**JSONL Format**: One JSON object per line with the same fields.

Example files are available in the project documentation.
""")
