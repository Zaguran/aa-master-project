import streamlit as st

# Nastavení stránky
st.set_page_config(page_title="AAT v0.2.0", layout="wide")

# Sidebar s verzí
st.sidebar.info("Nasazena verze: 0.2.0")

# Hlavní navigace (Taby)
tabs = st.tabs(["Dashboard", "Requirements (DNG)", "Traceability Matrix", "Code Review", "💬 Chat"])

# --- TAB DASHBOARD ---
with tabs[0]:
    st.title("Automotive Assistance Tool (AAT) v0.2.0")
    st.header("Systémový přehled")
    st.write("Vítejte v AAT. Toto je hlavní rozcestník pro správu kvality projektu.")
    st.success("Připojení k GitHub Actions: Aktivní (Zelená)")

# --- TAB REQUIREMENTS ---
with tabs[1]:
    st.header("Requirements (DNG)")
    st.write("Zde bude správa požadavků.")

# --- TAB TRACEABILITY ---
with tabs[2]:
    st.header("Traceability Matrix")
    st.write("Propojení požadavků a testů.")

# --- TAB CODE REVIEW ---
with tabs[3]:
    st.header("Code Review")
    st.write("Přehled revizí kódu.")

# --- TAB CHAT (NOVÝ) ---
with tabs[4]:
    st.header("💬 AI Asistent")
    st.info("Tady je Ollama, tvůj osobní asistent pro automotive projekty.")
    
    # Inicializace historie chatu (aby zprávy nezmizely při každém kliknutí)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Zobrazení historie zpráv
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Vstup od uživatele
    if prompt := st.chat_input("Napiš něco..."):
        # Zobrazení zprávy uživatele
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Odpověď asistenta (zatím statická, než propojíme skutečnou Ollamu)
        response = f"Ollama: Přijal jsem tvůj dotaz: '{prompt}'. Zatím jsem v testovacím režimu, ale brzy mě propojíme s tvou databází!"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
