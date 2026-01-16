import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import json

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT'),
        options="-c search_path=work_aa"
    )

def get_aa_stats():
    """Vrací statistiky tabulek pro Dashboard"""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        tables = ['projects', 'nodes', 'links', 'customer']
        stats = []
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()['count']
            stats.append({"Tabulka": table, "Počet záznamů": count})
        cur.close()
        conn.close()
        return stats
    except Exception as e:
        print(f"Chyba DB: {e}")
        return []

def get_table_data(table_name, limit=20, offset=0):
    """Vrací data konkrétní tabulky pro Table View"""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cur.fetchone()['count']
        cur.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows, total
    except Exception as e:
        return str(e), 0

def update_agent_heartbeat(agent_name: str, queue_size: int = 0, details: dict = None):
    """Update agent heartbeat in agent_status table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if details is None:
            details = {}
        
        cur.execute("""
            UPDATE agent_status
            SET last_heartbeat = now(),
                queue_size = %s,
                details = %s
            WHERE agent_name = %s
        """, (queue_size, json.dumps(details), agent_name))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error updating heartbeat for {agent_name}: {e}")

def list_agent_status():
    """List all agent status records."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT agent_name, status, last_heartbeat, queue_size, details
            FROM agent_status
            ORDER BY agent_name
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing agent status: {e}")
        return []

def agent_loop():
    """Tato funkce bude srdcem asynchronního agenta."""
    print("DB Bridge Agent startuje...")
    while True:
        try:
            # Zde bude později logika pro zpracování úkolů
            pass
        except Exception as e:
            print(f"Chyba agenta: {e}")
        time.sleep(30)

if __name__ == "__main__":
    agent_loop()