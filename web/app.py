import streamlit as st
import pandas as pd
import requests
from database import get_aa_stats, get_table_data

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# Konfigurace
VERSION = "0.51"
OLLAMA_URL_GENERATE = "http://localhost:11434/api/generate"
OLLAMA_URL_TAGS = "http://localhost:11434/api/tags"
OLLAMA_URL_PULL = "http://localhost:11434/api/pull"
OLLAMA_MODEL = "llama3"

def check_ollama():
    """Zkontroluje, zda Ollama běží a zda je model stažený."""
    try:
        resp = requests.get(OLLAMA_URL_TAGS, timeout=2)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            return True, models
        return False, []
    except:
        return False, []

def main():
    # --- SIDEBAR: Verze, Status a Ovládání ---
    with st.sidebar:
        st.title(f"Verze: {VERSION}")
        st.markdown("---")
        st.subheader("🤖 Ollama Status")
        
        is_online, installed_models = check_ollama()
        
        if is_online:
            st.success("● Online (API běží)")
            model_exists = any(OLLAMA_MODEL in m for m in installed_models)
            
            if model_exists:
                st.info(f"**Model:** {OLLAMA_MODEL} ✅")
            else:
                st.warning(f"**Model:** {OLLAMA_MODEL} ❌ (Nenalezen)")
                if st.button("📥 Load Model (Pull)"):
                    with st.spinner(f"Stahuji {OLLAMA_MODEL}..."):
                        try:
                            r = requests.post(OLLAMA_URL_PULL, json={"name": OLLAMA_MODEL, "stream": False})
                            st.rerun()
                        except:
                            st.error("Stažení selhalo.")
        else:
            st.error("● Offline (API nedostupné)")
            st.warning("Ujistěte se, že Ollama kontejner běží.")
            
        st.markdown(f"**Mód:** Generativní")
    
    st.title("🚀 AA Project Control Tower")
    
    # Původní taby zůstávají beze změny
    tabs = st.tabs(["💬 Chat s Ollamou", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])
    
    # --- TAB 1: CHAT S OLLAMOU ---
    with tabs[0]:
        st.header("Chat s AI (Ollama)")
        user_input = st.text_input("Zadej otázku pro model Llama 3:", key="ollama_chat")
        if st.button("Odeslat"):
            if user_input:
                with st.spinner("Přemýšlím..."):
                    try:
                        response = requests.post(OLLAMA_URL_GENERATE, json={
                            "model": OLLAMA_MODEL,
                            "prompt": user_input,
                            "stream": False
                        })
                        st.write(response.json().get("response", "Chyba odpovědi"))
                    except Exception as e:
                        st.error(f"Nelze se spojit s Ollamou: {e}")
            else:
                st.warning("Napiš nejdříve text.")

    # --- TAB 2: DASHBOARD ---
    with tabs[1]:
        st.header("Database Statistics")
        stats = get_aa_stats()
        if stats:
            st.table(pd.DataFrame(stats))
        else:
            st.error("Nepodařilo se načíst statistiky ze Serveru A.")

    # --- TAB 3: TABLE VIEW ---
    with tabs[2]:
        st.header("Table Data Explorer")
        table_name = st.selectbox("Vyber tabulku", ["projects", "nodes", "links", "customer"])
        data, total = get_table_data(table_name)
        if isinstance(data, list):
            st.write(f"Celkem záznamů: {total}")
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.error(f"Chyba připojení: {data}")

    # --- TAB 4: LOGS ---
    with tabs[3]:
        st.header("System Logs")
        st.info("Logy z agenta (Server A) se zde brzy objeví.")

if __name__ == "__main__":
    main()