import streamlit as st
import requests
import json

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AAT v0.3.1",
    page_icon="🚗",
    layout="wide"
)

# Sidebar
st.sidebar.title("AAT Ovládání")
st.sidebar.info("Nasazena verze: 0.3.1")

# --- FUNKCE PRO OLLAMU ---
def get_ollama_response(user_input):
    # Definice URL musí být UVNITŘ funkce, aby ji Python viděl
    url = "http://host.docker.internal:11434/api/generate"
    
    payload = {
        "model": "llama3.1:8b",
        "prompt": user_input,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=45)
        if response.status_code == 200:
            return response.json().get("response", "Chyba: Prázdná odpověď.")
        else:
            return f"⚠️ Chyba serveru Ollama: Kód {response.status_code}"
    except Exception as e:
        # Pokud se něco pokazí, vypíšeme přesnou chybu
        return f"❓ Chyba komunikace: {str(e)}"

# --- HLAVNÍ NAVIGACE (TABY) ---
tabs = st.tabs(["📊 Dashboard", "📑 Requirements", "🔗 Traceability", "🔍 Code Review", "💬 Chat s Ollamou"])

# 1. TAB: DASHBOARD
with tabs[0]:
    st.title("Automotive Assistance Tool (AAT) v0.3.1")
    st.header("Systémový přehled")
    st.success("✅ Aplikace běží v Dockeru")

# ... (ostatní taby 1, 2, 3 nechej prázdné nebo jak jsi měl) ...

# 5. TAB: CHAT
with tabs[4]:
    st.header("💬 AI Asistent (Ollama)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Zeptej se na něco..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Ollama přemýšlí..."):
                full_response = get_ollama_response(prompt)
                st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})