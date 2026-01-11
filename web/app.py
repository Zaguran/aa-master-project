import streamlit as st
import pandas as pd
import sys
import os

# Importujeme funkce přímo ze souboru database.py, 
# který bude nyní umístěn ve stejné složce jako tento skript.
from database import get_aa_stats, get_table_data

# Základní konfigurace stránky
st.set_page_config(
    page_title="AA Project Control Tower",
    page_icon="🚀",
    layout="wide"
)

def main():
    st.title("🚀 AA Project Control Tower")
    st.markdown("---")
    
    # Definice záložek
    tabs = st.tabs(["📊 Dashboard", "📅 Table View", "⚙️ Logs"])
    
    # --- ZÁLOŽKA DASHBOARD ---
    with tabs[0]:
        st.header("Database Statistics")
        stats = get_aa_stats()
        if stats:
            # Převedeme seznam slovníků na DataFrame pro hezké zobrazení
            df_stats = pd.DataFrame(stats)
            st.table(df_stats)
        else:
            st.error("Nepodařilo se načíst statistiky z databáze na Serveru A.")

    # --- ZÁLOŽKA TABLE VIEW ---
    with tabs[1]:
        st.header("Table Data Explorer")
        
        # Výběr tabulky
        table_name = st.selectbox(
            "Vyber tabulku pro zobrazení dat:", 
            ["projects", "nodes", "links", "customer"]
        )
        
        # Načtení dat z vybrané tabulky
        data, total = get_table_data(table_name)
        
        if isinstance(data, list):
            st.success(f"Zobrazeno prvních 20 záznamů z celkem {total}.")
            if len(data) > 0:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.info("Tabulka je momentálně prázdná.")
        else:
            st.error(f"Chyba při načítání dat: {data}")

    # --- ZÁLOŽKA LOGS ---
    with tabs[2]:
        st.header("System Logs")
        st.info("Zde se brzy objeví logy z agenta běžícího na Serveru A.")

if __name__ == "__main__":
    main()