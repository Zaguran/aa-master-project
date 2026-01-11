import streamlit as st
import pandas as pd
import requests
import sys
import os

# Přidání cesty k agentům, aby Streamlit viděl database.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'db_bridge'))
from database import get_aa_stats, get_table_data

# --- KONFIGURACE ---
st.set_page_config(page_title="AAT v0.4.0", page_icon="🚗", layout="wide")

st.sidebar.title("AAT Ovládání")
st.sidebar.info("Verze: 0.4.1 (Refactored)")
st.sidebar.write("🧠 **Model:** Llama 3.1 (8B)")

# --- HLAVNÍ MENU ---
tabs = st.tabs(["Dashboard", "Requirements", "Traceability", "Table View", "DB Status", "Chat"])

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.header("Systémový přehled")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Vítejte v AA Proof of Concept. Systém je připraven pro sémantickou analýzu.")
    with col2:
        st.metric(label="DB Schéma", value="work_aa")

# --- TAB: TABLE VIEW (Nové) ---
with tabs[3]:
    st.header("🔍 Data Explorer")
    target_table = st.selectbox("Vyberte tabulku k zobrazení:", 
                                ["projects", "nodes", "links", "customer", "ai_analysis"])
    
    # Session state pro stránkování
    if f"off_{target_table}" not in st.session_state:
        st.session_state[f"off_{target_table}"] = 0
    
    limit = 20
    rows, total = get_table_data(target_table, limit, st.session_state[f"off_{target_table}"])
    
    if isinstance(rows, str):
        st.error(f"Chyba DB: {rows}")
    else:
        st.write(f"Zobrazeno {len(rows)} z celkem {total} záznamů")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        
        c1, c2, _ = st.columns([1, 1, 5])
        with c1:
            if st.button("⬅️ Předchozí") and st.session_state[f"off_{target_table}"] >= limit:
                st.session_state[f"off_{target_table}"] -= limit
                st.rerun()
        with col2:
            if st.button("Další ➡️") and st.session_state[f"off_{target_table}"] + limit < total:
                st.session_state[f"off_{target_table}"] += limit
                st.rerun()

# --- TAB: DB STATUS (Nové) ---
with tabs[4]:
    st.header("📊 Database Status")
    stats_data = get_aa_stats()
    if stats_data:
        st.table(pd.DataFrame(stats_data))
    else:
        st.warning("Nepodařilo se načíst statistiky ze schématu work_aa.")

# --- TAB: CHAT (AI ASISTENT) ---
with tabs[5]:
    st.header("💬 AI Asistent (Ollama)")
    # (Zde zůstává tvoje původní logika chatu z app.py v0.3.4)
    st.info("Chat je připraven k použití.")