import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Control Tower", layout="wide")

# --- KONFIGURACE ---
OLLAMA_URL = "http://168.119.122.36:11434/api/generate"

if 'result' not in st.session_state: st.session_state.result = ""
if 'timer' not in st.session_state: st.session_state.timer = 0

st.title("🚀 Automotive Assistant: AI Extractor")

# --- VSTUPY ---
col1, col2 = st.columns([1, 1])

with col1:
    zakaznik = st.selectbox("Zákazník:", ["Škoda Auto", "BMW Group", "CARIAD", "Continental"])
    file = st.file_uploader("Vložte PDF specifikaci", type=['pdf'])

with col2:
    prompt = f"Analyze this document for {zakaznik}. Extract all requirements into a Markdown table with columns: ID, Title, Description. Keep it strictly in English."
    st.write("Nastavení: LLaVA | Temperature 0.7 | CPU 8-cores")
    run = st.button("SPUSTIT ANALÝZU ⚡", use_container_width=True)

st.divider()

# --- LOGIKA ---
if run and file:
    start = time.time()
    with st.spinner(f"Provádím analýzu pro {zakaznik}..."):
        # 1. Převod PDF na obrázek (DPI 150 pro rychlost kolem 90s)
        images = convert_from_bytes(file.read(), dpi=150)
        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='JPEG')
        
        # 2. Odeslání do Ollama
        payload = {
            "model": "llava",
            "prompt": prompt,
            "stream": False,
            "images": [base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')],
            "options": {"temperature": 0.7} # Nastavení pro nejlepší pochopení tabulky
        }
        
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=300)
            st.session_state.result = r.json().get("response", "Žádná data nebyla vrácena.")
            st.session_state.timer = round(time.time() - start, 2)
        except Exception as e:
            st.error(f"Chyba spojení se serverem: {e}")

# --- VÝSTUP ---
if st.session_state.result:
    st.info(f"⏱ Dokument zdigitalizován za {st.session_state.timer} sekund")
    st.markdown(f"### Výsledek pro: {zakaznik}")
    st.markdown(st.session_state.result)
    
    if st.button("Vymazat výsledek"):
        st.session_state.result = ""
        st.rerun()