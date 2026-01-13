import streamlit as st
import pandas as pd
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

VERSION = "0.9"
OLLAMA_IP = "168.119.122.36"
OLLAMA_URL_GENERATE = f"http://{OLLAMA_IP}:11434/api/generate"
OLLAMA_URL_TAGS = f"http://{OLLAMA_IP}:11434/api/tags"

MODEL_TEXT = "llama3"
MODEL_VISION = "llava"

# Inicializace session state, aby výsledek nezmizel při překliku
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = ""
if 'process_time' not in st.session_state:
    st.session_state.process_time = 0

def check_ollama():
    try:
        resp = requests.get(OLLAMA_URL_TAGS, timeout=5)
        return (True, [m['name'] for m in resp.json().get('models', [])]) if resp.status_code == 200 else (False, [])
    except: return False, []

is_online, _ = check_ollama()

# --- SIDEBAR ---
with st.sidebar:
    st.title(f"Verze: {VERSION}")
    st.subheader("🤖 Ollama Status")
    if is_online:
        st.success("● Online")
        st.info(f"Modul: {MODEL_VISION}\nMód: OCR & Extraction")
    else:
        st.error("● Offline")

# --- HLAVNÍ ČÁST ---
st.title("🚀 AA Project Control Tower")

# SEKVENCE 1: VSTUPY
st.markdown("### 1. Příprava dokumentu")
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("Nahraj PDF nebo Obrázek", type=['png', 'jpg', 'jpeg', 'pdf'])

with col2:
    user_input = st.text_area("Instrukce pro AI:", 
                              value="Extract all requirements (ID|Title|Description) in a table. Keep it strictly in English.",
                              height=100)
    send_btn = st.button("Spustit analýzu ⚡")

st.markdown("---")

# SEKVENCE 2: VÝSLEDEK
st.markdown("### 2. Výsledek analýzy")

if send_btn and is_online and user_input:
    start_time = time.time()
    payload = {"model": MODEL_TEXT, "prompt": user_input, "stream": False}

    if uploaded_file:
        payload["model"] = MODEL_VISION
        with st.spinner("📷 Převádím dokument a analyzuji pixely..."):
            if uploaded_file.type == "application/pdf":
                images = convert_from_bytes(uploaded_file.read())
                buffered = io.BytesIO()
                images[0].save(buffered, format="JPEG")
                img_byte = buffered.getvalue()
            else:
                img_byte = uploaded_file.getvalue()
            
            payload["images"] = [base64.b64encode(img_byte).decode('utf-8')]

    try:
        r = requests.post(OLLAMA_URL_GENERATE, json=payload)
        st.session_state.ai_result = r.json().get("response", "Chyba.")
        st.session_state.process_time = round(time.time() - start_time, 2)
    except Exception as e:
        st.error(f"Chyba: {e}")

# Zobrazení výsledku (zůstane vidět i po interakci s jinými prvky)
if st.session_state.ai_result:
    st.info(f"⏱ Čas zpracování: {st.session_state.process_time} sekund")
    st.markdown(st.session_state.ai_result)
    
    # Bonus: Tlačítko pro vymazání
    if st.button("Vymazat výsledek"):
        st.session_state.ai_result = ""
        st.rerun()