import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

# --- METADATA (Dle zdrojů [2] a [3]) ---
PROJECT_ID = "AAT-2026-POC"
VERSION = "1.0.0"
OLLAMA_URL = "http://168.119.122.36:11434/api/generate"

st.set_page_config(page_title="AA Control Tower", layout="wide")

# --- OPRAVA CHYBY STARTU (Řádek 41) ---
# Definujeme dva sloupce v poměru 1:1, jak bylo v původním app.txt [1]
st.title("🚀 Automotive Assistant: AI Extractor")
col1, col2 = st.columns(2) 

# --- STAV SERVERU ---
def check_ollama():
    try:
        requests.get("http://168.119.122.36:11434", timeout=2)
        return True
    except: return False

is_online = check_ollama()

# --- VSTUPY (Levý sloupec) ---
with col1:
    st.subheader("Vstupní data")
    zakaznik = st.selectbox("Zákazník:", ["Škoda Auto", "BMW Group", "CARIAD", "Continental"])
    file = st.file_uploader("Vložte PDF specifikaci (Requirements Specification.pdf)", type=['pdf'])

# --- KONFIGURACE (Pravý sloupec) ---
with col2:
    st.subheader("Parametry analýzy")
    # Prompt upraven pro SYS-REQ-004 (ID, Title, Description, Status) [4, 5]
    prompt = (
        f"Analyze document for {zakaznik}. "
        "Extract all requirements into a Markdown table with columns: "
        "ID, Title, Description, Status. Strictly English. No talk."
    )
    st.info(f"Model: LLaVA | Teplota: 0.1 | Stav: {'ONLINE' if is_online else 'OFFLINE'}")
    run = st.button("SPUSTIT KOMPLETNÍ DIGITALIZACI ⚡", type="primary", disabled=not is_online)

st.divider()

# --- LOGIKA DIGITALIZACE VŠECH STRAN ---
if run and file:
    start_time = time.time()
    all_pages_output = []
    
    with st.spinner("Digitalizuji všechny strany dokumentu..."):
        # Převedeme PDF na obrázky (všechny strany) [6]
        pdf_bytes = file.read()
        images = convert_from_bytes(pdf_bytes, dpi=120)
        
        progress_bar = st.progress(0)
        
        for i, img in enumerate(images):
            # Informujeme uživatele o postupu
            progress_bar.progress((i + 1) / len(images))
            
            # Příprava obrázku pro AI
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            # Payload pro Ollama (Snížená teplota proti halucinacím) [6]
            payload = {
                "model": "llava",
                "prompt": prompt,
                "stream": False,
                "images": [img_b64],
                "options": {"temperature": 0.1}
            }

            try:
                # Zvýšený timeout na 600s pro eliminaci chyby ze snímku obrazovky [7]
                r = requests.post(OLLAMA_URL, json=payload, timeout=600)
                if r.status_code == 200:
                    res = r.json().get("response", "")
                    all_pages_output.append(f"### Strana {i+1}\n{res}")
                else:
                    st.error(f"Chyba na straně {i+1} (Status {r.status_code})")
            except Exception as e:
                st.error(f"Timeout nebo chyba spojení na straně {i+1}: {e}")

    # --- ZOBRAZENÍ VÝSLEDKŮ ---
    st.success(f"Analýza dokončena za {round(time.time() - start_time, 2)} s")
    final_md = "\n\n".join(all_pages_output)
    st.markdown(final_md)