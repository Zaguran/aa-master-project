import streamlit as st
import requests
import json

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AAT v0.3.2",
    page_icon="🚗",
    layout="wide"
)

# Sidebar s verzí
st.sidebar.title("AAT Ovládání")
st.sidebar.info("Nasazena verze: 0.3.2")
st.sidebar.write("🧠 **Model:** Llama 3.1 (8B)")

# --- FUNKCE PRO OLLAMU ---
def get_ollama_response(user_input):
    # V režimu network_mode: host používáme 127.0.0.1, 
    # protože kontejner sdílí síť přímo se serverem.
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": user_input,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        if response.status_code == 200:
            return response.json().get("response", "Chyba: Prázdná odpověď.")
        else:
            return f"⚠️ Chyba serveru Ollama: Kód {response.status_code}"
    except Exception as e:
        return f"❌ Chyba komunikace: {str(e)}"

# --- HLAVNÍ NAVIGACE (VŠECHNY TABY) ---
tabs = st.tabs([
    "📊 Dashboard", 
    "📑 Requirements", 
    "🔗 Traceability", 
    "🔍 Code Review", 
    "💬 Chat s Ollamou"
])

# 1. TAB: DASHBOARD
with tabs[0]:
    st.title("Automotive Assistance Tool (AAT) v0.3.2")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Systémový přehled")
        st.write("Vítejte v AAT. Toto je hlavní rozcestník pro správu kvality projektu.")
        st.success("✅ Provoz: Docker (Host Network)")
    with col2:
        st.header("Statistiky")
        st.metric(label="Dostupnost AI", value="Online (127.0.0.1)")

# 2. TAB: REQUIREMENTS
with tabs[1]:
    st.header("Requirements (DNG)")
    st.info("Sekce v přípravě pro v0.4.0.")

# 3. TAB: TRACEABILITY
with tabs[2]:
    st.header("Traceability Matrix")
    st.write("Modul pro propojení testů a požadavků.")

# 4. TAB: CODE REVIEW
with tabs[3]:
    st.header("Code Review")
    st.write("Statická analýza kódu.")

# 5. TAB: CHAT (AI ASISTENT)
with tabs[4]:
    st.header("💬 AI Asistent (Ollama)")
    st.info("Tady je Ollama, tvůj osobní asistent běžící přímo na tvém serveru.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Zeptej se Ollamy..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Ollama přemýšlí..."):
                full_response = get_ollama_response(prompt)
                st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})