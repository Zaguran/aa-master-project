import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

# --- KONFIGURACE A METADATA (Zdroj [1], [2]) ---
PROJECT_ID = "AAT-2026-POC"
VERSION = "1.0.0"
OLLAMA_URL = "http://168.119.122.36:11434/api/generate"
OLLAMA_CHECK = "http://168.119.122.36:11434/api/tags"

st.set_page_config(page_title=f"AA Control Tower {PROJECT_ID}", layout="wide")

# --- FUNKCE PRO KONTROLU SPOJENÍ ---
def is_server_online():
    try:
        response = requests.get(OLLAMA_CHECK, timeout=5)
        return response.status_code == 200
    except:
        return False

# --- UI - HLAVIČKA ---
st.title("🚀 Automotive Assistant: AI Extractor")
st.caption(f"Projekt: {PROJECT_ID} | Verze: {VERSION}")

# OPRAVA: Definice sloupců pro rozhraní (Oprava chyby unpacking) [2]
col1, col2 = st.columns(2)

# --- VSTUPY (Levý sloupec) ---
with col1:
    st.subheader("Vstupní data")
    zakaznik = st.selectbox("Zákazník:", ["Cust_1", "Cust_2", "Cust_3", "Cust_4"])
    file = st.file_uploader("Vložte PDF specifikaci (Requirements Specification.pdf)", type=['pdf'])

# --- KONFIGURACE (Pravý sloupec) ---
with col2:
    st.subheader("Parametry analýzy")
    # Prompt upraven dle SYS-REQ-004: ID, Title, Description, Status, Link [3], [4]
    prompt_text = (
        f"Analyze this document for {zakaznik}. "
        "Extract all requirements into a Markdown table with EXACTLY these columns: "
        "ID, Title, Description, Status (New/Original/Modified), External Link (URL). "
        "Keep it strictly in English. No introductory text, only the table."
    )
    
    server_status = is_server_online()
    if server_status:
        st.success("Ollama Status: ONLINE")
    else:
        st.error("Ollama Status: OFFLINE (Zkontrolujte spojení na 168.119.122.36)")
    
    st.info("Model: LLaVA | Teplota: 0.1 (Precizní) | Timeout: 600s")
    run = st.button("SPUSTIT KOMPLETNÍ ANALÝZU ⚡", use_container_width=True, disabled=not server_status)

st.divider()

# --- LOGIKA DIGITALIZACE (Zpracování všech stran) [3], [5] ---
if run and file:
    start_total = time.time()
    all_results = []
    
    with st.spinner(f"Analyzuji dokument pro {zakaznik}..."):
        # 1. Převod všech stran PDF na obrázky (Oprava: kód už nebere jen images) [5]
        pdf_bytes = file.read()
        images = convert_from_bytes(pdf_bytes, dpi=140)
        
        progress_bar = st.progress(0)
        
        for i, page_image in enumerate(images):
            progress_bar.progress((i + 1) / len(images))
            
            # Příprava obrázku pro odeslání
            img_byte_arr = io.BytesIO()
            page_image.save(img_byte_arr, format='JPEG')
            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            # 2. Odeslání do Ollama (Oprava: Teplota 0.1 a zvýšený timeout) [6], [5]
            payload = {
                "model": "llava",
                "prompt": prompt_text,
                "stream": False,
                "images": [base64_image],
                "options": {"temperature": 0.1} 
            }

            try:
                # Navýšení na 600s kvůli dřívějšímu selhání (read timeout=300) [6]
                response = requests.post(OLLAMA_URL, json=payload, timeout=600)
                
                if response.status_code == 200:
                    extracted_text = response.json().get("response", "")
                    all_results.append(f"## Strana {i+1}\n{extracted_text}")
                else:
                    all_results.append(f"## Strana {i+1}\nChyba serveru: {response.status_code}")
            
            except Exception as e:
                st.error(f"Chyba při komunikaci na straně {i+1}: {e}")

    # --- VÝSTUPNÍ DASHBOARD ---
    total_duration = round(time.time() - start_total, 2)
    st.success(f"Analýza dokončena za {total_duration} sekund")
    
    # Zobrazení všech výsledků pod sebou
    final_markdown = "\n\n".join(all_results)
    st.markdown(final_markdown)

    # Možnost resetu [7]
    if st.button("Vymazat a začít znovu"):
        st.rerun()