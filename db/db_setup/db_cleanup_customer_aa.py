
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
db_cleanup_customer.py
Deletes Customer_* projects and their linked nodes, links, and ai_analysis entries.

Uses ONLY environment variables:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

Schema: work_aa
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

SCHEMA = "work_aa"

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        options=f"-c search_path={SCHEMA}"
    )

def cleanup_customer_data():
    conn = get_conn()
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("=== CLEANUP: Removing Customer_* projects ===")

    # 1) Najdi všechny projekty zákazníka
    cur.execute("SELECT project_id FROM projects WHERE project_id LIKE 'Customer_%'")
    projects = [row["project_id"] for row in cur.fetchall()]

    if not projects:
        print("No Customer_* projects found. Nothing to delete.")
        return

    for pid in projects:
        print(f" - Removing project: {pid}")

        # Smazání linků ke všem nodům v projektu
        cur.execute("""
            DELETE FROM links
            WHERE source_uuid IN (
                SELECT node_uuid FROM nodes WHERE project_id=%s
            )
            OR target_uuid IN (
                SELECT node_uuid FROM nodes WHERE project_id=%s
            );
        """, (pid, pid))

        # Smazání ai_analysis
        cur.execute("""
            DELETE FROM ai_analysis
            WHERE node_uuid IN (
                SELECT node_uuid FROM nodes WHERE project_id=%s
            );
        """, (pid,))

        # Smazání nodes
        cur.execute("DELETE FROM nodes WHERE project_id=%s;", (pid,))

        # Smazání projektu
        cur.execute("DELETE FROM projects WHERE project_id=%s;", (pid,))

    print("DONE: Customer data cleaned.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    cleanup_customer_data()
