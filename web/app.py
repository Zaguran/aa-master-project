import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.5.3"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_BASE = f"http://{OLLAMA_IP}:11434"

OLLAMA_URL_GENERATE = f"{OLLAMA_URL_BASE}/api/generate"
OLLAMA_URL_TAGS = f"{OLLAMA_URL_BASE}/api/tags"
OLLAMA_URL_PULL = f"{OLLAMA_URL_BASE}/api/pull"
OLLAMA_MODEL = "llama3"

def check_ollama():
    try:
        resp = requests.get(OLLAMA_URL_TAGS, timeout=5)
        if resp.status_code == 200:
            models_data = resp.json().get('models', [])
            return True, [m['name'] for m in models_data]
        return False, []
    except:
        return False, []

def main():
    with st.sidebar:
        st.title(f"Verze: {VERSION}")
        st.markdown("---")
        st.subheader("🤖 Ollama Service")
        is_online, installed_models = check_ollama()
        
        if is_online:
            st.success("● Online")
            if any(OLLAMA_MODEL in m for m in installed_models):
                st.info(f"**Model:** {OLLAMA_MODEL} ✅")
            else:
                st.warning(f"**Model:** {OLLAMA_MODEL} ❌")
                if st.button("📥 Load Model"):
                    requests.post(OLLAMA_URL_PULL, json={"name": OLLAMA_MODEL, "stream": False})
                    st.rerun()
        else:
            st.error("● Offline")
        st.markdown("**Mód:** Generativní")

    st.title("🚀 AA Project Control Tower")
    tabs = st.tabs(["💬 Chat", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])

    with tabs[0]:
        st.header("Chat s AI")
        user_input = st.text_input("Zadej otázku:", key="chat_in")
        if st.button("Odeslat"):
            if user_input and is_online:
                with st.spinner("..."):
                    try:
                        # Odstraněn problematický timeout a složité options pro build
                        r = requests.post(OLLAMA_URL_GENERATE, json={
                            "model": OLLAMA_MODEL,
                            "prompt": user_input,
                            "stream": False
                        })
                        st.write(r.json().get("response", "Prázdná odpověď"))
                    except Exception as e:
                        st.error(f"Chyba: {e}")

    # Dashboard, Table View a Logs zůstávají beze změny (přebírají se z database.py)
    with tabs[1]:
        st.header("Database Statistics")
        from database import get_aa_stats
        s = get_aa_stats()
        if s: st.table(pd.DataFrame(s))
    
    with tabs[2]:
        st.header("Table Data Explorer")
        from database import get_table_data
        t = st.selectbox("Tabulka", ["projects", "nodes", "links", "customer"])
        d, total = get_table_data(t)
        if isinstance(d, list): st.dataframe(pd.DataFrame(d))

if __name__ == "__main__":
    main()