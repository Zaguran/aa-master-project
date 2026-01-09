import streamlit as st
import requests
import json

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AAT v0.3.4",
    page_icon="🚗",
    layout="wide"
)

# Sidebar s verzí
st.sidebar.title("AAT Ovládání")
st.sidebar.info("Nasazena verze: 0.3.4")
st.sidebar.write("🧠 **Model:** Llama 3.1 (8B)")
st.sidebar.write("⚡ **Režim:** Streaming")

# --- FUNKCE PRO OLLAMU SE STREAMINGEM ---
def get_ollama_response(user_input):
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": user_input,
        "stream": True  # Povolujeme streaming na straně Ollamy
    }
    
    full_response = ""
    # Vytvoříme prázdný box v UI, do kterého budeme sypat text
    message_placeholder = st.empty()
    
    try:
        # Nastavíme stream=True i pro HTTP požadavek
        with requests.post(url, json=payload, timeout=300, stream=True) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    # Dekódujeme řádek z JSONu
                    chunk = json.loads(line.decode('utf-8'))
                    token = chunk.get("response", "")
                    full_response += token
                    
                    # Okamžitě aktualizujeme UI (přidáme kurzor pro efekt)
                    message_placeholder.markdown(full_response + "▌")
                    
                    if chunk.get("done"):
                        break
        
        # Po skončení vypíšeme finální text bez kurzoru
        message_placeholder.markdown(full_response)
        return full_response

    except Exception as e:
        error_msg = f"❌ Chyba komunikace: {str(e)}"
        st.error(error_msg)
        return error_msg

# --- HLAVNÍ NAVIGACE ---
tabs = st.tabs([
    "📊 Dashboard", 
    "📑 Requirements", 
    "🔗 Traceability", 
    "🔍 Code Review", 
    "💬 Chat s Ollamou"
])

# 1. TAB: DASHBOARD
with tabs[0]:
    st.title("Automotive Assistance Tool (AAT) v0.3.4")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Systémový přehled")
        st.write("Vítejte v AAT. AI asistent je nyní připojen v režimu streamování.")
        st.success("✅ Provoz: Docker (Host Network)")
    with col2:
        st.header("Statistiky")
        st.metric(label="Dostupnost AI", value="Online (Streaming)")

# 2. - 4. TAB: (Zatím prázdné)
with tabs[1]: st.header("Requirements (DNG)")
with tabs[2]: st.header("Traceability Matrix")
with tabs[3]: st.header("Code Review")

# 5. TAB: CHAT (AI ASISTENT)
with tabs[4]:
    st.header("💬 AI Asistent (Ollama)")
    
    # Inicializace historie zpráv
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Zobrazení historie zpráv
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Vstup od uživatele
    if prompt := st.chat_input("Zeptej se na CAN bus, ISO 26262 nebo cokoliv..."):
        # Uložíme dotaz do historie
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generování odpovědi
        with st.chat_message("assistant"):
            # Zavoláme naši streamovací funkci
            full_ans = get_ollama_response(prompt)
            
        # Uložíme hotovou odpověď do historie
        st.session_state.messages.append({"role": "assistant", "content": full_ans})