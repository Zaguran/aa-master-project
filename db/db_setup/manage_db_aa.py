import os
import psycopg2
from psycopg2 import Error
import logging
import json

# Version: 1.4.5.6 - Final fix for agents import with dual sys.path and __init__.py files

# Nastavení logování
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT')
    )

def check_table_content(cur, schema_name, table_name):
    """Vypíše počet záznamů a ukázku dat pro danou tabulku."""
    try:
        cur.execute(f'SELECT COUNT(*) FROM {schema_name}.{table_name};')
        total_count = cur.fetchone()[0]
        logger.info(f"[{table_name}] Celkem záznamů: {total_count}")
        
        if total_count > 0:
            cur.execute(f'SELECT * FROM {schema_name}.{table_name} LIMIT 5;')
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            logger.info(f"  -> Ukázka dat (prvních 5):")
            for row in rows:
                # Převede řádek na čitelný formát (zkrátí dlouhé texty)
                readable_row = [str(val)[:50] + "..." if isinstance(val, str) and len(str(val)) > 50 else val for val in row]
                logger.info(f"     {dict(zip(colnames, readable_row))}")
    except Exception as e:
        logger.warning(f"  -> Nelze přečíst obsah tabulky {table_name}: {e}")

def init_aa_structure():
    conn = None
    schema_name = "work_aa"
    tables = ["customer", "projects", "nodes", "links", "ai_analysis", "agent_status", "system_health"]
    
    try:
        conn = get_connection()
        conn.autocommit = True
        cur = conn.cursor()

        logger.info(f"=== INICIALIZACE SCHÉMATU {schema_name.upper()} ===")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
        cur.execute(f"SET search_path TO {schema_name};")

        # --- DEFINICE TABULEK (Zkráceno pro přehlednost, kód stejný jako dříve) ---
        cur.execute("CREATE TABLE IF NOT EXISTS customer (customer_id VARCHAR(50) PRIMARY KEY, full_name VARCHAR(255), contact VARCHAR(255));")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id VARCHAR(100) PRIMARY KEY,
                type VARCHAR(50), 
                status VARCHAR(50), 
                customer_id VARCHAR(50) REFERENCES customer(customer_id),
                parent_platform_id VARCHAR(100) REFERENCES projects(project_id),
                baseline_version VARCHAR(50),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                project_id VARCHAR(100) REFERENCES projects(project_id),
                type VARCHAR(50),
                scope VARCHAR(50),
                inheritance VARCHAR(50),
                asil VARCHAR(10),
                test_level VARCHAR(50),
                node_status VARCHAR(50),
                content TEXT,
                attributes JSONB,
                version VARCHAR(50),
                processing_status INT DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS links (
                link_id SERIAL PRIMARY KEY,
                source_uuid UUID REFERENCES nodes(node_uuid) ON DELETE CASCADE,
                target_uuid UUID REFERENCES nodes(node_uuid) ON DELETE CASCADE,
                link_type VARCHAR(50),
                ai_match_score FLOAT DEFAULT 0.0,
                manual_override BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                analysis_id SERIAL PRIMARY KEY,
                node_uuid UUID REFERENCES nodes(node_uuid) ON DELETE CASCADE,
                analysis_type VARCHAR(50),
                result_json JSONB,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # --- AUTHENTICATION TABLES (v1.3.0) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_user (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_role (
                role_id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_user_role (
                user_id UUID REFERENCES app_user(user_id) ON DELETE CASCADE,
                role_id INT REFERENCES app_role(role_id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, role_id)
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_session (
                session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES app_user(user_id) ON DELETE CASCADE,
                expires_at TIMESTAMPTZ NOT NULL,
                csrf_token TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now(),
                revoked BOOLEAN DEFAULT FALSE
            );
        """)
        
        # --- AGENT STATUS TABLE (v1.4.4) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_name TEXT PRIMARY KEY,
                status TEXT DEFAULT 'READY',
                last_heartbeat TIMESTAMPTZ,
                queue_size INT DEFAULT 0,
                details JSONB DEFAULT '{}'
            );
        """)
        
        # --- SYSTEM HEALTH TABLE (v1.4.4) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_health (
                metric_id SERIAL PRIMARY KEY,
                node_name TEXT NOT NULL,
                cpu_usage FLOAT,
                ram_usage FLOAT,
                disk_usage FLOAT,
                timestamp TIMESTAMPTZ DEFAULT now()
            );
        """)

        # --- POMOCNÉ INDEXY ---
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_project ON nodes(project_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_uuid);")

        # --- DEFAULT DATA ---
        cur.execute("INSERT INTO projects (project_id, type, status, baseline_version) VALUES ('Platforma_A', 'PLATFORM', 'ACTIVE', 'v1.0.0') ON CONFLICT DO NOTHING;")
        
        # --- AUTH DEFAULT DATA ---
        cur.execute("INSERT INTO app_role(name) VALUES ('admin') ON CONFLICT (name) DO NOTHING;")
        cur.execute("INSERT INTO app_role(name) VALUES ('visitor') ON CONFLICT (name) DO NOTHING;")
        
        # --- AGENT STATUS SEED DATA (v1.4.4) ---
        agents = [
            'pdf_extractor',
            'pdf_chunker',
            'strict_extractor',
            'embedding_agent',
            'matching_agent',
            'trace_agent',
            'report_agent',
            'git_impact_agent',
            'bridge_api',
            'monitor_db_server',
            'monitor_ollama_server'
        ]
        for agent in agents:
            cur.execute(
                "INSERT INTO agent_status (agent_name, status, queue_size) VALUES (%s, 'READY', 0) ON CONFLICT (agent_name) DO NOTHING;",
                (agent,)
            )

        # --- SELF-CHECK OBSAHU ---
        logger.info("=== KONTROLA OBSAHU TABULEK ===")
        for table in tables:
            check_table_content(cur, schema_name, table)

        logger.info(f"=== MANAGE_DB_AA.PY FINISHED ===")

    except (Exception, Error) as error:
        logger.error(f"KRITICKÁ CHYBA: {error}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_aa_structure()