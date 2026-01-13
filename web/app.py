import streamlit as st
import pandas as pd
import requests
import base64
import io
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.8"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_BASE = f"http://{OLLAMA_IP}:11434"
OLLAMA_URL_GENERATE = f"{OLLAMA_URL_BASE}/api/generate"
OLLAMA_URL_TAGS = f"{OLLAMA_URL_BASE}/api/tags"

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
            st.write(f"**Moduly:** {MODEL_TEXT} / {MODEL_VISION}")
            st.write(f"**Mód:** OCR & Analýza PDF")
        else:
            st.error("● Offline")

    st.title("🚀 AA Project Control Tower")
    tabs = st.tabs(["💬 Chat & Vision", "📊 Dashboard", "📅 Table View"])

    with tabs[0]:
        st.header("Analýza dokumentů (PDF & Obrázky)")
        uploaded_file = st.file_uploader("Nahraj dokument pro extrakci požadavků", type=['png', 'jpg', 'jpeg', 'pdf'])
        user_input = st.text_input("Instrukce pro AI (např. 'Vypiš ID a popis požadavků'):", key="chat_in")
        
        if st.button("Odeslat") and is_online:
            if user_input:
                payload = {"model": MODEL_TEXT, "prompt": user_input, "stream": False}

                if uploaded_file is not None:
                    payload["model"] = MODEL_VISION
                    with st.spinner("Zpracovávám dokument..."):
                        # --- LOGIKA PRO PDF KONVERZI ---
                        if uploaded_file.type == "application/pdf":
                            # Převod první stránky PDF na obrázek
                            images = convert_from_bytes(uploaded_file.read())
                            buffered = io.BytesIO()
                            images[0].save(buffered, format="JPEG")
                            img_byte = buffered.getvalue()
                        else:
                            img_byte = uploaded_file.getvalue()
                        
                        base64_image = base64.b64encode(img_byte).decode('utf-8')
                        payload["images"] = [base64_image]

                with st.spinner(f"AI analyzuje pomocí {payload['model']}..."):
                    try:
                        r = requests.post(OLLAMA_URL_GENERATE, json=payload)
                        st.markdown("### Výsledek analýzy:")
                        st.write(r.json().get("response", "Chyba při zpracování."))
                    except Exception as e:
                        st.error(f"Spojení s Ollama selhalo: {e}")

    # Dashboard a Table View zůstávají propojeny na tvou SQL databázi 
    with tabs[1]:
        st.header("Database Statistics")
        try:
            from database import get_aa_stats
            st.table(pd.DataFrame(get_aa_stats()))
        except: st.info("Data nejsou k dispozici.")

if __name__ == "__main__":
    main()