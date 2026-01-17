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

def insert_or_update_platform_requirement(req: dict):
    """
    Insert or update platform requirement in nodes table.
    Expected keys: req_id, text, type, priority, asil, owner, version, baseline, status
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        attributes = {
            "req_id": req.get("req_id"),
            "type": req.get("type"),
            "priority": req.get("priority"),
            "owner": req.get("owner"),
            "baseline": req.get("baseline")
        }

        # Check if exists
        cur.execute("""
            SELECT node_uuid FROM nodes
            WHERE project_id = 'Platform_A'
              AND scope = 'platform'
              AND attributes->>'req_id' = %s
        """, (req.get("req_id"),))

        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE nodes SET
                    content = %s,
                    asil = %s,
                    version = %s,
                    node_status = %s,
                    attributes = %s
                WHERE node_uuid = %s
            """, (
                req.get("text"),
                req.get("asil"),
                req.get("version"),
                req.get("status"),
                json.dumps(attributes),
                existing["node_uuid"]
            ))
        else:
            cur.execute("""
                INSERT INTO nodes (project_id, type, scope, content, asil, version, node_status, attributes)
                VALUES ('Platform_A', 'requirement', 'platform', %s, %s, %s, %s, %s)
            """, (
                req.get("text"),
                req.get("asil"),
                req.get("version"),
                req.get("status"),
                json.dumps(attributes)
            ))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error inserting/updating platform requirement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def insert_or_update_customer_requirement(customer_id: str, req: dict):
    """
    Insert or update customer requirement in nodes table.
    Expected keys: req_id, text, priority, source_doc
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        project_id = f"Customer_{customer_id}"
        attributes = {
            "req_id": req.get("req_id"),
            "priority": req.get("priority"),
            "source_doc": req.get("source_doc")
        }

        cur.execute("""
            SELECT node_uuid FROM nodes
            WHERE project_id = %s
              AND scope = 'customer'
              AND attributes->>'req_id' = %s
        """, (project_id, req.get("req_id")))

        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE nodes SET
                    content = %s,
                    attributes = %s
                WHERE node_uuid = %s
            """, (
                req.get("text"),
                json.dumps(attributes),
                existing["node_uuid"]
            ))
        else:
            cur.execute("""
                INSERT INTO nodes (project_id, type, scope, content, attributes)
                VALUES (%s, 'requirement', 'customer', %s, %s)
            """, (
                project_id,
                req.get("text"),
                json.dumps(attributes)
            ))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error inserting/updating customer requirement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def create_customer_project(customer_id: str):
    """Create customer project in projects table."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        project_id = f"Customer_{customer_id}"

        cur.execute("""
            INSERT INTO projects (project_id, type, status)
            VALUES (%s, 'CUSTOMER', 'ACTIVE')
            ON CONFLICT (project_id) DO NOTHING
        """, (project_id,))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error creating customer project: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def list_projects():
    """List all projects ordered by project_id."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM projects ORDER BY project_id")
        rows = cur.fetchall()

        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing projects: {e}")
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