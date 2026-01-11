import streamlit as st
import pandas as pd
import requests
from database import get_aa_stats, get_table_data

st.set_page_config(page_title="AA Project Control Tower", layout="wide", page_icon="🚀")

# Konfigurace Ollama (Server B)
OLLAMA_URL = "http://localhost:11434/api/generate" # Předpokládáme, že Ollama běží na stejném serveru jako web

def main():
    st.title("🚀 AA Project Control Tower")
    
    # Všechny taby pohromadě
    tabs = st.tabs(["💬 Chat s Ollamou", "📊 Dashboard", "📅 Table View", "⚙️ Logs"])
    
    # --- TAB 1: CHAT S OLLAMOU ---
    with tabs[0]:
        st.header("Chat s AI (Ollama)")
        user_input = st.text_input("Zadej otázku pro model Llama 3:")
        if st.button("Odeslat"):
            if user_input:
                with st.spinner("Přemýšlím..."):
                    try:
                        response = requests.post(OLLAMA_URL, json={
                            "model": "llama3",
                            "prompt": user_input,
                            "stream": False
                        })
                        st.write(response.json().get("response", "Chyba odpovědi"))
                    except Exception as e:
                        st.error(f"Nelze se spojit s Ollamou: {e}")
            else:
                st.warning("Napiš nejdříve text.")

    # --- TAB 2: DASHBOARD ---
    with tabs[1]:
        st.header("Database Statistics")
        stats = get_aa_stats()
        if stats:
            st.table(pd.DataFrame(stats))
        else:
            st.error("Nepodařilo se načíst statistiky ze Serveru A.")

    # --- TAB 3: TABLE VIEW ---
    with tabs[2]:
        st.header("Table Data Explorer")
        table_name = st.selectbox("Vyber tabulku", ["projects", "nodes", "links", "customer"])
        data, total = get_table_data(table_name)
        if isinstance(data, list):
            st.write(f"Celkem záznamů: {total}")
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.error(f"Chyba připojení: {data}")

    # --- TAB 4: LOGS ---
    with tabs[3]:
        st.header("System Logs")
        st.info("Logy z agenta (Server A) se zde brzy objeví.")

if __name__ == "__main__":
    main()