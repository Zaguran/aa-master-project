import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.7"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_BASE = f"http://{OLLAMA_IP}:11434"

OLLAMA_URL_GENERATE = f"{OLLAMA_URL_BASE}/api/generate"
OLLAMA_URL_TAGS = f"{OLLAMA_URL_BASE}/api/tags"
OLLAMA_URL_PULL = f"{OLLAMA_URL_BASE}/api/pull"

# Modely
MODEL_TEXT = "llama3"
MODEL_VISION = "llava"

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
    is_online, installed_models = check_ollama()
    
    with st.sidebar:
        st.title(f"Verze: {VERSION}")
        st.markdown("---")
        st.subheader("🤖 Ollama Service")
        
        if is_online:
            st.success("● Online")
            # Požadavek z 11.01.2026: Zobrazení verze modulu a módu
            st.write(f"**Modul:** {MODEL_TEXT} / {MODEL_VISION}")
            st.write(f"**Mód:** OCR & Generativní")
            
            # Kontrola přítomnosti modelů
            if not any(MODEL_VISION in m for m in installed_models):
                st.warning(f"Chybí vision model ({MODEL_VISION})")
                if st.button("📥 Stáhnout Vision Modul"):
                    requests.post(OLLAMA_URL_PULL, json={"name": MODEL_VISION, "stream": False})
                    st.rerun()
        else:
            st.error("● Offline")

    st.title("🚀 AA Project Control Tower")
    tabs = st.tabs(["💬 Chat & Vision", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])

    with tabs[0]:
        st.header("AI Asistent (Text + Obrázky)")
        
        # Nahrávání souborů
        uploaded_file = st.file_uploader("Nahraj obrázek (nebo PDF - experimentální)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        user_input = st.text_input("Zadej instrukci (např. 'Převeď tabulku na text'):", key="chat_in")
        
        if st.button("Odeslat"):
            if user_input and is_online:
                payload = {
                    "model": MODEL_TEXT,
                    "prompt": user_input,
                    "stream": False
                }

                # Logika pro obrázky
                if uploaded_file is not None:
                    if uploaded_file.type == "application/pdf":
                        st.warning("Poznámka: Přímé zpracování PDF vyžaduje konverzi na obrázky. Zkouším extrahovat text přes vision model...")
                    
                    # Přepnutí na vision model
                    payload["model"] = MODEL_VISION
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    payload["images"] = [base64_image]

                with st.spinner(f"Analyzuji pomocí {payload['model']}..."):
                    try:
                        r = requests.post(OLLAMA_URL_GENERATE, json=payload)
                        st.markdown("### Výsledek analýzy:")
                        st.write(r.json().get("response", "Prázdná odpověď"))
                    except Exception as e:
                        st.error(f"Chyba: {e}")

    with tabs[1]:
        st.header("Database Statistics")
        try:
            from database import get_aa_stats
            s = get_aa_stats()
            if s: st.table(pd.DataFrame(s))
        except:
            st.info("Statistiky momentálně nejsou dostupné.")
    
    with tabs[2]:
        st.header("Table Data Explorer")
        try:
            from database import get_table_data
            t = st.selectbox("Tabulka", ["projects", "nodes", "links", "customer"])
            d, total = get_table_data(t)
            if isinstance(d, list): st.dataframe(pd.DataFrame(d))
        except:
            st.info("Průzkumník dat není dostupný.")

if __name__ == "__main__":
    main()