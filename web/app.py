import streamlit as st
import requests
import json

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AAT v0.3.0",
    page_icon="🚗",
    layout="wide"
)

# Sidebar s informacemi
st.sidebar.title("AAT Ovládání")
st.sidebar.info("Nasazena verze: 0.3.0")
st.sidebar.markdown("---")
st.sidebar.write("🚀 **Status:** Dockerized")
st.sidebar.write("🧠 **Model:** Llama 3.1 (8B)")

# --- FUNKCE PRO OLLAMU ---
def get_ollama_response(user_input):
    """
    Komunikace s Ollamou běžící na hostitelském serveru.
    IP 172.17.0.1 je výchozí brána Dockeru k hostiteli.
    """
    url = "http://172.17.0.1:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": user_input,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=45)
        if response.status_code == 200:
            return response.json().get("response", "Chyba: Prázdná odpověď od modelu.")
        else:
            return f"⚠️ Chyba serveru Ollama: Kód {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Chyba připojení: Ollama neběží nebo je špatně nastavená IP (zkus 172.17.0.1)."
    except Exception as e:
        return f"❓ Neočekávaná chyba: {str(e)}"

# --- HLAVNÍ NAVIGACE (TABY) ---
tabs = st.tabs([
    "📊 Dashboard", 
    "📑 Requirements", 
    "🔗 Traceability", 
    "🔍 Code Review", 
    "💬 Chat s Ollamou"
])

# 1. TAB: DASHBOARD
with tabs[0]:
    st.title("Automotive Assistance Tool (AAT) v0.2.0")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Systémový přehled")
        st.write("Vítejte v AAT. Toto je hlavní rozcestník pro správu kvality projektu.")
        st.success("✅ Připojení k GitHub Actions: Aktivní")
    with col2:
        st.header("Statistiky")
        st.metric(label="Aktivní uzly", value="1 (Hetzner VPS)")
        st.metric(label="Dostupnost AI", value="Online (Port 11434)")

# 2. TAB: REQUIREMENTS
with tabs[1]:
    st.header("Requirements (DNG)")
    st.warning("Tato sekce je v přípravě pro v0.3.0.")
    st.write("Zde bude správa požadavků a importy z IBM DOORS Next Gen.")

# 3. TAB: TRACEABILITY
with tabs[2]:
    st.header("Traceability Matrix")
    st.write("Automatické propojení požadavků, designu a testovacích scénářů.")

# 4. TAB: CODE REVIEW
with tabs[3]:
    st.header("Code Review & Static Analysis")
    st.write("Přehled revizí kódu a výstupy z nástrojů jako QAC nebo Polyspace.")

# 5. TAB: CHAT (AI ASISTENT)
with tabs[4]:
    st.header("💬 AI Asistent (Ollama)")
    st.info("Tady je tvůj osobní asistent. Běží lokálně na tvém Hetzner serveru.")

    # Inicializace historie zpráv v session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Zobrazení historie zpráv
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Vstup uživatele
    if prompt := st.chat_input("Zeptej se na něco ohledně automotive standardů..."):
        # Přidání zprávy uživatele do historie
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generování odpovědi od AI
        with st.chat_message("assistant"):
            with st.spinner("Ollama (Llama 3.1) přemýšlí..."):
                full_response = get_ollama_response(prompt)
                st.markdown(full_response)
        
        # Přidání odpovědi AI do historie
        st.session_state.messages.append({"role": "assistant", "content": full_response})