import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Control Tower | POC Demo", layout="wide", page_icon="🚀")

VERSION = "0.9.4 (Demo)"
OLLAMA_URL = "http://168.119.122.36:11434/api/generate"
MODEL_VISION = "llava"

if 'ai_result' not in st.session_state: st.session_state.ai_result = ""
if 'run_time' not in st.session_state: st.session_state.run_time = 0

# --- STYLOVÁNÍ PRO ŠÉFA ---
st.markdown("""
    <style>
    .report-box { padding: 20px; border-radius: 10px; border: 1px solid #e6e9ef; background-color: #f0f2f6; }
    .metric-text { font-size: 24px; font-weight: bold; color: #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/rocket.png", width=80)
    st.title(f"Control Tower v{VERSION}")
    st.write("---")
    st.success("Ollama: Connected (Hetzner VM)")
    if st.button("Resetovat rozhraní"):
        st.session_state.ai_result = ""
        st.rerun()

st.title("🛡️ Automotive Assistant: AI Extractor")
st.info("Demo mód pro extrakci systémových požadavků (SYS-REQ) z dokumentace.")

# --- VSTUP ---
col_u, col_p = st.columns([1, 1])
with col_u:
    uploaded_file = st.file_uploader("Nahrajte specifikaci (PDF)", type=['pdf'])
with col_p:
    # Prompt vyladěný na výkon a angličtinu
    prompt = (
        "You are a requirements engineer. Extract the table of requirements from this image. "
        "Create a Markdown table: ID | Title | Description. "
        "STRICTLY IN ENGLISH. Do not translate. Output ONLY the table."
    )
    st.caption("AI Konfigurace: Temperature 0.7 | DPI 150")
    run_btn = st.button("SPUSTIT AI ANALÝZU ⚡", use_container_width=True)

st.divider()

# --- LOGIKA ---
if run_btn and uploaded_file:
    start = time.time()
    with st.status("🚀 AI Agent pracuje...", expanded=True) as status:
        # Krok 1: Rychlá digitalizace
        status.write("Digitalizace dokumentu...")
        images = convert_from_bytes(uploaded_file.read(), dpi=150) # Nižší DPI = vyšší rychlost
        buf = io.BytesIO()
        images[0].save(buf, format="JPEG", quality=85)
        
        # Krok 2: Analýza
        status.write("Extrakce požadavků pomocí LLaVA...")
        payload = {
            "model": MODEL_VISION,
            "prompt": prompt,
            "stream": False,
            "images": [base64.b64encode(buf.getvalue()).decode('utf-8')],
            "options": {"temperature": 0.7, "num_thread": 8}
        }
        
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=200)
            st.session_state.ai_result = r.json().get("response", "")
            st.session_state.run_time = round(time.time() - start, 2)
            status.update(label=f"Analýza hotova za {st.session_state.run_time}s!", state="complete")
        except:
            st.error("Chyba spojení se serverem.")

# --- VÝSLEDEK ---
if st.session_state.ai_result:
    st.subheader("📊 Extrahovaná data (AAT-2026-POC)")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Status", "Success")
    c2.metric("Čas", f"{st.session_state.run_time} s")
    c3.metric("Zdroj", "Local LLM")

    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.markdown(st.session_state.ai_result)
    st.markdown('</div>', unsafe_allow_html=True)