import os
import psycopg2
from psycopg2 import Error
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_connection():
    """Connect to trading database with work_aa schema."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT'),
        options="-c search_path=work_aa"
    )

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_auth_tables():
    """Create authentication tables in work_aa schema."""
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        logger.info("=== CREATING AUTH TABLES IN work_aa SCHEMA ===")
        
        # Table: app_user
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
        logger.info("✓ Table app_user created")
        
        # Table: app_role
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_role (
                role_id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        """)
        logger.info("✓ Table app_role created")
        
        # Table: app_user_role
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_user_role (
                user_id UUID REFERENCES app_user(user_id) ON DELETE CASCADE,
                role_id INT REFERENCES app_role(role_id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, role_id)
            );
        """)
        logger.info("✓ Table app_user_role created")
        
        # Table: app_session
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
        logger.info("✓ Table app_session created")
        
        # Insert default roles
        cur.execute("INSERT INTO app_role(name) VALUES ('admin') ON CONFLICT (name) DO NOTHING;")
        cur.execute("INSERT INTO app_role(name) VALUES ('visitor') ON CONFLICT (name) DO NOTHING;")
        logger.info("✓ Default roles created (admin, visitor)")
        
        # Create default admin user
        admin_email = "admin@aat.local"
        admin_password = "admin123"
        admin_hash = hash_password(admin_password)
        
        cur.execute("""
            INSERT INTO app_user (email, full_name, password_hash, is_active)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING user_id;
        """, (admin_email, "System Administrator", admin_hash, True))
        
        result = cur.fetchone()
        if result:
            admin_user_id = result[0]
            logger.info(f"✓ Admin user created: {admin_email}")
            
            # Assign admin role
            cur.execute("SELECT role_id FROM app_role WHERE name = 'admin';")
            admin_role_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO app_user_role (user_id, role_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (admin_user_id, admin_role_id))
            logger.info(f"✓ Admin role assigned to {admin_email}")
        else:
            logger.info(f"ℹ Admin user {admin_email} already exists")
        
        logger.info("=== AUTH TABLES SETUP COMPLETE ===")
        logger.info(f"Default credentials: {admin_email} / {admin_password}")
        
        cur.close()
        
    except (Exception, Error) as error:
        logger.error(f"ERROR: {error}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_auth_tables()
