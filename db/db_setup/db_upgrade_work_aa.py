
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
db_upgrade_work_aa.py
Adds new PoC tables into schema work_aa, idempotent and safe.

Uses ONLY env variables:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

SCHEMA = "work_aa"

AGENTS = [
    "pdf_extractor",
    "pdf_chunker",
    "strict_extractor",
    "embedding_agent",
    "matching_agent",
    "trace_agent",
    "report_agent",
    "git_impact_agent",
    "bridge_api",
    "monitor_db_server",
    "monitor_ollama_server"
]

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        options=f"-c search_path={SCHEMA}"
    )

def upgrade():
    conn = get_conn()
    conn.autocommit = True
    cur = conn.cursor()
   
    # PŘIDEJTE TENTO ŘÁDEK:
    print("Enabling pgvector extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    print("=== UPGRADE: Creating new PoC tables if missing ===")

    # --- Embedding Model Registry ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_embedding_model (
        model_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        dims INT NOT NULL,
        framework TEXT DEFAULT 'ollama',
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- Requirement Embeddings ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS req_embedding (
        emb_id BIGSERIAL PRIMARY KEY,
        model_id INT REFERENCES ai_embedding_model(model_id),
        source_type TEXT NOT NULL,
        source_id TEXT NOT NULL,
        project_id TEXT,
        platform_id TEXT,
        rfq_id TEXT,
        lang TEXT,
        text_hash TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding vector(768),
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ
    );
    """)

    # --- Matching Results ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS req_match (
        match_id BIGSERIAL PRIMARY KEY,
        model_id INT REFERENCES ai_embedding_model(model_id),
        rfq_id TEXT,
        platform_id TEXT,
        customer_req_id TEXT,
        platform_req_id TEXT,
        cosine_similarity DOUBLE PRECISION,
        rank INT,
        method TEXT DEFAULT 'pgvector.cosine',
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- Platform Traceability ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS platform_trace (
        platform_req_id TEXT PRIMARY KEY,
        has_system BOOLEAN DEFAULT FALSE,
        has_arch BOOLEAN DEFAULT FALSE,
        has_code BOOLEAN DEFAULT FALSE,
        has_test BOOLEAN DEFAULT FALSE,
        tests_passed BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- Git Events ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS code_change_event (
        event_id BIGSERIAL PRIMARY KEY,
        repo TEXT,
        branch TEXT,
        commit_before TEXT,
        commit_after TEXT,
        author TEXT,
        files JSONB,
        status TEXT DEFAULT 'NEW',
        created_at TIMESTAMPTZ DEFAULT now(),
        processed_at TIMESTAMPTZ
    );
    """)

    # --- Git Impact ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS code_impact (
        impact_id BIGSERIAL PRIMARY KEY,
        repo TEXT,
        commit_after TEXT,
        file_path TEXT,
        code_id TEXT,
        platform_req_id TEXT,
        similarity DOUBLE PRECISION,
        impact_level TEXT,
        signal_source TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- Hints from code (REQ-ID, DNG-ID, etc.) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS code_link_hint (
        hint_id BIGSERIAL PRIMARY KEY,
        repo TEXT,
        commit_after TEXT,
        file_path TEXT,
        line_no INT,
        token TEXT,
        matched_req_id TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- RFQ ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rfq (
        rfq_id TEXT PRIMARY KEY,
        customer_id TEXT,
        project_id TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- RFQ Reports ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rfq_report (
        rfq_id TEXT PRIMARY KEY,
        platform_id TEXT,
        summary_html TEXT,
        pdf_path TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # --- Agent Status ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_status (
        agent_name TEXT PRIMARY KEY,
        status TEXT DEFAULT 'READY',
        last_heartbeat TIMESTAMPTZ,
        queue_size INT DEFAULT 0,
        details JSONB DEFAULT '{}'
    );
    """)

    # Insert agents if missing
    for agent in AGENTS:
        cur.execute("""
        INSERT INTO agent_status (agent_name)
        VALUES (%s)
        ON CONFLICT (agent_name) DO NOTHING;
        """, (agent,))

    # --- System Health ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS system_health (
        node_name TEXT PRIMARY KEY,
        cpu FLOAT,
        ram FLOAT,
        disk FLOAT,
        timestamp TIMESTAMPTZ,
        raw JSONB
    );
    """)

    print("DONE: New tables added or already existed.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    upgrade()
