import streamlit as st
import requests
import base64
import io
import time
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AA Control Tower", layout="wide", page_icon="🚀")

# --- KONFIGURACE ---
VERSION = "0.9.8"
OLLAMA_URL = "http://168.119.122.36:11434/api/generate"

# Inicializace session state
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'ai_result' not in st.session_state: st.session_state.ai_result = ""

# --- BOČNÍ MENU (SIDEBAR) ---
with st.sidebar:
    st.title(f"Control Tower v{VERSION}")
    st.write("---")
    st.success("● Ollama: Connected")
    st.info("Model: LLaVA (Vision)\nMode: Expert Extraction")
    
    st.write("---")
    # Tlačítko pro reset kontextu - tvůj požadavek
    if st.button("🗑️ RESET KONTEXTU / CLEAR", use_container_width=True):
        st.session_state.ai_result = ""
        st.session_state.chat_history = []
        st.rerun()

# --- HLAVNÍ ROZHRANÍ ---
st.title("🛡️ AA Project Control Tower")

# Nahrávání souboru
uploaded_file = st.file_uploader("Nahrajte PDF nebo obrázek specifikace", type=['pdf', 'png', 'jpg'])

# Chatovací okno s přednastaveným promptem
# Pokud stiskneš šipku dolů nebo začneš psát, můžeš použít toto:
default_prompt = "Extract all requirements from the document. Output a Markdown table with columns: ID | Title | Description. Keep it strictly in English as in the source. Do not provide any introduction, only the table."

user_query = st.text_area("Chat s AI / Instrukce:", value=default_prompt, height=150)

col_run, col_timer = st.columns([1, 1])
with col_run:
    run_btn = st.button("ODESLAT DOTAZ / ANALÝZU ⚡", use_container_width=True)

# --- LOGIKA EXTRAKCE ---
if run_btn and uploaded_file:
    start_time = time.time()
    with st.status("🚀 AI Agent analyzuje dokument...", expanded=True) as status:
        
        # Digitalizace PDF na obrázek (dpi 150 pro rychlost kolem 90s)
        status.write("📸 Digitalizace stránek...")
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read(), dpi=150)
            buf = io.BytesIO()
            images[0].save(buf, format="JPEG")
            img_data = buf.getvalue()
        else:
            img_data = uploaded_file.getvalue()

        # Dotaz na Ollama
        status.write("🧠 Extrakce požadavků (LLaVA)...")
        payload = {
            "model": "llava",
            "prompt": user_query,
            "stream": False,
            "images": [base64.b64encode(img_data).decode('utf-8')],
            "options": {"temperature": 0.3} # Snížená teplota pro přesnost SYS-REQ
        }
        
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=300)
            if r.status_code == 200:
                st.session_state.ai_result = r.json().get("response", "")
                st.session_state.process_time = round(time.time() - start_time, 2)
                status.update(label=f"Hotovo za {st.session_state.process_time}s!", state="complete")
            else:
                st.error("Chyba serveru Ollama.")
        except Exception as e:
            st.error(f"Spojení selhalo: {e}")

# --- ZOBRAZENÍ VÝSLEDKU ---
if st.session_state.ai_result:
    st.markdown("---")
    st.subheader("📊 Výsledek analýzy")
    st.metric("Čas zpracování", f"{st.session_state.process_time} s")
    
    with st.container(border=True):
        st.markdown(st.session_state.ai_result)