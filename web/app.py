import streamlit as st

# Nastavení stránky
st.set_page_config(page_title="AA Tool - Automotive Assistance", layout="wide")

# Verze aplikace
VERSION = "0.2.0"

st.title(f"Automotive Assistance Tool (AAT) v{VERSION}")
st.sidebar.info(f"Nasazena verze: {VERSION}")

# Definice tabů pro budoucí funkcionality
tabs = st.tabs(["Dashboard", "Requirements (DNG)", "Traceability Matrix", "Code Review"])

with tabs[0]:
    st.header("Systémový přehled")
    st.write("Vítejte v AAT. Toto je hlavní rozcestník pro správu kvality projektu.")
    st.success("Připojení k GitHub Actions: Aktivní (Zelená)")

with tabs[1]:
    st.header("Requirements Management")
    st.info("Zde budeme simulovat rozhraní DOORS Next Generation.")
    # Sem později přidáme tabulku s req, co máš připravené

with tabs[2]:
    st.header("Traceability Matrix")
    st.write("Vazby mezi zákaznickými požadavky a implementací v C.")

with tabs[3]:
    st.header("AI Code Review")
    st.write("Analýza souladu kódu s požadavky pomocí Gemini/Ollama.")

# Konec souboru