import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

# --- METADATA A KONFIGURACE  ---
PROJECT_ID = "AAT-2026-POC"
VERSION = "1.0"
OLLAMA_BASE_URL = "http://168.119.122.36:11434"
MODEL_NAME = "llava"

st.set_page_config(page_title=f"AA Control Tower v{VERSION}", layout="wide")

# --- POMOCNÉ FUNKCE ---
def check_ollama_status():
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# --- UI - HLAVIČKA ---
st.title("🚀 Automotive Assistant: AI Extractor")

# Zobrazení stavových informací na webu
col_meta1, col_meta2, col_meta3 = st.columns(3)
with col_meta1:
    st.metric("Project ID", PROJECT_ID)
with col_meta2:
    st.metric("Version", VERSION)
with col_meta3:
    is_online = check_ollama_status()
    status_label = "ONLINE" if is_online else "OFFLINE"
    st.write(f"**Ollama Status:** :{'green' if is_online else 'red'}[{status_label}]")
    st.caption(f"Host: {OLLAMA_BASE_URL}")

# --- VSTUPY ---
col1, col2 = st.columns([3])

with col1:
    zakaznik = st.selectbox("Zákazník:", ["Cust_1", "Cust_2", "Cust_3", "Cust_4"])
    file = st.file_uploader("Vložte PDF specifikaci", type=['pdf'])

with col2:
    # Upravený prompt dle SYS-REQ-004: ID, Title, Description, Status, 
    prompt = (
        f"Analyze this document for {zakaznik}. "
        "Extract all requirements into a Markdown table with columns: "
        "ID, Title, Description, Status, External Link. "
        "Keep it strictly in English. Do not translate. "
        "If no requirements are on the page, return only: 'No requirements found'."
    )
    st.info("**Nastavení:** LLaVA (Vision) | Teplota: 0.1 | Timeout: 600s")
    run = st.button("SPUSTIT KOMPLETNÍ ANALÝZU ⚡", use_container_width=True, disabled=not is_online)

st.divider()

# --- LOGIKA ZPRACOVÁNÍ  ---
if run and file:
    start_total = time.time()
    all_results = []
    
    with st.spinner(f"Digitalizace a analýza všech stran pro {zakaznik}..."):
        # 1. Převod všech stran PDF na obrázky 
        pdf_content = file.read()
        images = convert_from_bytes(pdf_content, dpi=150)
        
        progress_bar = st.progress(0)
        
        for i, page_image in enumerate(images):
            # Aktualizace postupu
            progress_bar.progress((i + 1) / len(images))
            
            # Příprava obrázku pro danou stranu
            img_byte_arr = io.BytesIO()
            page_image.save(img_byte_arr, format='JPEG')
            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            # 2. Odeslání do Ollama 
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "images": [base64_image],
                "options": {"temperature": 0.1} # Sníženo z 0.7 pro eliminaci halucinací 
            }

            try:
                # Navýšen timeout na 600s kvůli chybě 'Read timed out' 
                r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=600)
                if r.status_code == 200:
                    page_response = r.json().get("response", "")
                    all_results.append(f"### Strana {i+1}\n{page_response}")
                else:
                    all_results.append(f"### Strana {i+1}\nChyba serveru: {r.status_code}")
            except Exception as e:
                st.error(f"Chyba na straně {i+1}: {e}")

    # --- VÝSTUP  ---
    total_time = round(time.time() - start_total, 2)
    st.success(f"✅ Kompletní dokument zdigitalizován za {total_time} sekund")
    
    final_output = "\n\n".join(all_results)
    st.markdown(f"## Finální digitální specifikace: {zakaznik}")
    st.markdown(final_output)
    
    # Možnost resetu
    if st.button("Vymazat výsledek"):
        st.session_state.result = ""
        st.rerun()