"""
Embeddings Generation Page
Version: 1.8
Generate vector embeddings for requirements
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from components import auth, session, layout
from components.embedding import generate_embeddings

st.set_page_config(page_title="Embeddings", page_icon="🧠", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/99_Login_Logout.py")
    st.stop()

# Admin only
auth.require_role(["admin"])

layout.render_header("Embeddings Generation")
st.title("🧠 Generate Embeddings")

st.markdown("---")

# Instructions
with st.expander("ℹ️ About Embeddings", expanded=False):
    st.markdown("""
    **Embeddings** are vector representations of text that capture semantic meaning.

    - Uses Ollama's **nomic-embed-text** model (768 dimensions)
    - Required for AI-powered matching between requirements
    - Generates embeddings for all requirements (customer + platform)
    - Skips already-embedded content (deduplication by hash)

    **Process:**
    1. Select scope (Customer, Platform, or All)
    2. Click Generate
    3. Wait for processing (may take time for large datasets)
    4. Review results
    """)

st.markdown("---")

# Configuration
st.subheader("⚙️ Configuration")

col1, col2 = st.columns(2)

with col1:
    scope = st.selectbox(
        "Scope",
        options=["all", "customer", "platform"],
        help="Which requirements to process"
    )

with col2:
    batch_size = st.number_input(
        "Batch Size",
        min_value=10,
        max_value=100,
        value=50,
        help="Number of requirements to process in one run"
    )

st.markdown("---")

# Generate button
if st.button("🚀 Generate Embeddings", type="primary", use_container_width=True):
    with st.spinner(f"Generating embeddings for {scope} requirements..."):
        try:
            result = generate_embeddings(
                scope=scope,
                model='nomic-embed-text',
                batch_size=batch_size
            )

            # Display results
            st.success("✅ Embedding generation completed!")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Embedded", result.get('embedded', 0))
            with col2:
                st.metric("Skipped", result.get('skipped', 0))
            with col3:
                st.metric("Errors", result.get('errors', 0))

            if result.get('errors', 0) > 0:
                st.warning("⚠️ Some requirements failed to embed. Check logs for details.")

        except Exception as e:
            st.error(f"❌ Error generating embeddings: {str(e)}")
            with st.expander("Error Details"):
                st.code(str(e))

st.markdown("---")

# Current status
st.subheader("📊 Current Embedding Status")

from agents.db_bridge.database import get_connection
from psycopg2.extras import RealDictCursor

try:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Count embeddings by scope
    cur.execute("""
        SELECT n.scope, COUNT(e.embedding_id) as count
        FROM embeddings e
        JOIN nodes n ON e.node_uuid = n.node_uuid
        GROUP BY n.scope
    """)

    results = cur.fetchall()

    if results:
        import pandas as pd
        df = pd.DataFrame(results)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(df, use_container_width=True, hide_index=True)

        with col2:
            total = df['count'].sum()
            st.metric("Total Embeddings", total)
    else:
        st.info("No embeddings generated yet")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Error loading status: {e}")
