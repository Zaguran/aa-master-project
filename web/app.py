import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.5.1"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_BASE = f"http://{OLLAMA_IP}:11434"

OLLAMA_URL_GENERATE = f"{OLLAMA_URL_BASE}/api/generate"
OLLAMA_URL_TAGS = f"{OLLAMA_URL_BASE}/api/tags"
OLLAMA_URL_PULL = f"{OLLAMA_URL_BASE}/api/pull"
OLLAMA_MODEL = "llama3"

def check_ollama():
    try:
        resp = requests.get(OLLAMA_URL_TAGS, timeout=3)
        if resp.status_code == 200:
            models_data = resp.json().get('models', [])
            models = [m['name'] for m in models_data] if models_data else []
            return True, models
        return False, []
    except Exception:
        return False, []

def main():
    # --- SIDEBAR: Verze, Status a Ovládání ---
    with st.sidebar:
        st.title(f"Verze: {VERSION}")
        st.markdown("---")
        st.subheader("🤖 Ollama Service")
        
        is_online, installed_models = check_ollama()
        
        if is_online:
            st.success("● Online (API dostupné)")
            model_exists = any(OLLAMA_MODEL in m for m in installed_models)
            
            if model_exists:
                st.info(f"**Model:** {OLLAMA_MODEL} ✅")
            else:
                st.warning(f"**Model:** {OLLAMA_MODEL} ❌ (Nenalezen)")
                if st.button("📥 Load Model (Pull)"):
                    with st.spinner(f"Stahuji model {OLLAMA_MODEL}..."):
                        try:
                            r = requests.post(OLLAMA_URL_PULL, json={"name": OLLAMA_MODEL, "stream": False})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Stažení selhalo: {e}")
        else:
            st.error("● Offline (API neodpovídá)")
            st.warning(f"Zkontrolujte IP {OLLAMA_IP}")
            
        st.markdown(f"**Mód:** Generativní")
    
    st.title("🚀 AA Project Control Tower")
    
    tabs = st.tabs(["💬 Chat s Ollamou", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])
    
    # --- TAB 1: CHAT S OLLAMOU ---
    with tabs[0]:
        st.header("Chat s AI (Ollama)")
        user_input = st.text_input("Zadej otázku pro model Llama 3:", key="ollama_chat")
        
        if st.button("Odeslat"):
            if user_input:
                if not is_online:
                    st.error("Ollama je offline.")
                else:
                    with st.spinner("Model generuje odpověď..."):
                        try:
                            # Posíláme JSON s vypnutým streamováním pro okamžitou odpověď
                            payload = {
                                "model": OLLAMA_MODEL,
                                "prompt": user_input,
                                "stream": False,
                                "options": {
                                    "num_predict": 128 # Omezíme délku pro rychlost testu
                                }
                            }
                            response = requests.post(OLLAMA_URL_GENERATE, json=payload, timeout=30)
                            
                            if response.status_code == 200:
                                result = response.json()
                                answer = result.get("response", "")
                                if answer:
                                    st.write("### Odpověď:")
                                    st.write(answer)
                                else:
                                    st.warning("Model vrátil prázdný text. Zkuste jinou otázku.")
                            else:
                                st.error(f"Chyba API ({response.status_code}): {response.text}")
                                
                        except Exception as e:
                            st.error(f"Chyba komunikace: {e}")
            else:
                st.warning("Napiš nejdříve text.")

    # --- Ostatní taby zůstávají beze změn (z database.py) ---
    with tabs[1]:
        st.header("Database Statistics")
        from database import get_aa_stats
        stats = get_aa_stats()
        if stats: st.table(pd.DataFrame(stats))
        else: st.error("Nepodařilo se načíst statistiky.")

    with tabs[2]:
        st.header("Table Data Explorer")
        from database import get_table_data
        table_name = st.selectbox("Vyber tabulku", ["projects", "nodes", "links", "customer"])
        data, total = get_table_data(table_name)
        if isinstance(data, list):
            st.write(f"Celkem záznamů: {total}")
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else: st.error(f"Chyba DB: {data}")

    with tabs[3]:
        st.header("System Logs")
        st.info("Logy z agenta (Server A) se zde brzy objeví.")

if __name__ == "__main__":
    main()