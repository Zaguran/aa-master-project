import streamlit as st
import pandas as pd
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

VERSION = "0.9.2"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL = f"http://{OLLAMA_IP}:11434/api/generate"

MODEL_VISION = "llava"

if 'ai_result' not in st.session_state:
    st.session_state.ai_result = ""
if 'process_time' not in st.session_state:
    st.session_state.process_time = 0

st.title("🚀 AA Project Control Tower")

with st.sidebar:
    st.title(f"Verze: {VERSION}")
    st.info("Mód: Přesná extrakce (v0.9.2)")
    # Tlačítko pro tvrdý restart paměti
    if st.button("Resetovat paměť AI"):
        st.session_state.ai_result = ""
        st.rerun()

st.markdown("### 1. Vstupní dokument")
uploaded_file = st.file_uploader("Nahrajte PDF specifikaci", type=['pdf', 'png', 'jpg'])
user_input = st.text_area("Prompt:", 
    "Look at the uploaded image. Extract the table with SYS-REQ IDs, Titles, and Descriptions. "
    "Output ONLY a Markdown table in English. Do not hallucinate about Indian laws.")

if st.button("Spustit analýzu ⚡"):
    if uploaded_file:
        start_time = time.time()
        status = st.status("Probíhá hloubková analýza...", expanded=True)
        
        # Fáze 1: Kvalitní konverze (DPI 200 pro lepší čitelnost)
        status.write("📸 Digitalizace PDF stránek...")
        if uploaded_file.type == "application/pdf":
            # Zvyšujeme DPI pro lepší OCR výsledky llava modelu
            images = convert_from_bytes(uploaded_file.read(), dpi=200)
            buffered = io.BytesIO()
            images[0].save(buffered, format="JPEG", quality=95)
            img_byte = buffered.getvalue()
        else:
            img_byte = uploaded_file.getvalue()
        
        # Fáze 2: Odeslání s parametry pro přesnost
        status.write("🧠 Model LLaVA čte tabulku (tento proces trvá ~150s)...")
        payload = {
            "model": MODEL_VISION,
            "prompt": user_input,
            "stream": False,
            "images": [base64.b64encode(img_byte).decode('utf-8')],
            "options": {
                "temperature": 0.1,  # Snížení kreativity pro přesná data
                "num_predict": 1000  # Dostatek místa pro celou tabulku
            }
        }
        
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=300)
            st.session_state.ai_result = r.json().get("response", "Chyba.")
            st.session_state.process_time = round(time.time() - start_time, 2)
            status.update(label="✅ Analýza dokončena!", state="complete")
        except Exception as e:
            st.error(f"Timeout nebo chyba spojení: {e}")

st.markdown("---")
st.markdown("### 2. Výsledek z dokumentu")

if st.session_state.ai_result:
    st.info(f"⏱ Čas zpracování: {st.session_state.process_time} sekund")
    st.markdown(st.session_state.ai_result)