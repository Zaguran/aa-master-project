import streamlit as st
import pandas as pd
import requests
from database import get_aa_stats, get_table_data

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.5"
# Ollama běží jako služba na této IP
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_BASE = f"http://{OLLAMA_IP}:11434"

OLLAMA_URL_GENERATE = f"{OLLAMA_URL_BASE}/api/generate"
OLLAMA_URL_TAGS = f"{OLLAMA_URL_BASE}/api/tags"
OLLAMA_URL_PULL = f"{OLLAMA_URL_BASE}/api/pull"
OLLAMA_MODEL = "llama3"

def check_ollama():
    """Zkontroluje, zda je Ollama API dostupné a vypíše seznam modelů."""
    try:
        resp = requests.get(OLLAMA_URL_TAGS, timeout=3)
        if resp.status_code == 200:
            # Získáme jména všech stažených modelů
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
            
            # Kontrola, zda je konkrétní model (např. llama3) v seznamu
            model_exists = any(OLLAMA_MODEL in m for m in installed_models)
            
            if model_exists:
                st.info(f"**Model:** {OLLAMA_MODEL} ✅")
            else:
                st.warning(f"**Model:** {OLLAMA_MODEL} ❌ (Nenalezen)")
                # Tlačítko pro stažení modelu, pokud chybí
                if st.button("📥 Load Model (Pull)"):
                    with st.spinner(f"Stahuji model {OLLAMA_MODEL} na server..."):
                        try:
                            r = requests.post(OLLAMA_URL_PULL, json={"name": OLLAMA_MODEL, "stream": False})
                            if r.status_code == 200:
                                st.success("Model stažen!")
                                st.rerun()
                            else:
                                st.error(f"Chyba při stahování: {r.status_code}")
                        except Exception as e:
                            st.error(f"Stažení selhalo: {e}")
        else:
            st.error("● Offline (API na IP neodpovídá)")
            st.warning(f"Zkontrolujte, zda Ollama běží na {OLLAMA_IP} a portu 11434.")
            
        st.markdown(f"**Mód:** Generativní")
    
    st.title("🚀 AA Project Control Tower")
    
    # Taby projektu
    tabs = st.tabs(["💬 Chat s Ollamou", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])
    
    # --- TAB 1: CHAT S OLLAMOU ---
    with tabs[0]:
        st.header("Chat s AI (Ollama)")
        user_input = st.text_input("Zadej otázku pro model Llama 3:", key="ollama_chat")
        
        if st.button("Odeslat"):
            if user_input:
                if not is_online:
                    st.error("Nelze odeslat dotaz, Ollama je offline.")
                else:
                    with st.spinner("Přemýšlím..."):
                        try:
                            response = requests.post(OLLAMA_URL_GENERATE, json={
                                "model": OLLAMA_MODEL,
                                "prompt": user_input,
                                "stream": False
                            })
                            answer = response.json().get("response", "Chyba: Prázdná odpověď od modelu.")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"Chyba při komunikaci: {e}")
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
            st.error(f"Chyba připojení k DB: {data}")

    # --- TAB 4: LOGS ---
    with tabs[3]:
        st.header("System Logs")
        st.info("Logy z agenta (Server A) se zde brzy objeví.")

if __name__ == "__main__":
    main()