import os
import psycopg2
from psycopg2.extras import RealDictCursor
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

def read_users():
    """Read and display all users with their roles."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("=== USER LIST ===")
        
        # Get all users with their roles
        cur.execute("""
            SELECT 
                u.user_id,
                u.email,
                u.full_name,
                u.is_active,
                u.created_at,
                ARRAY_AGG(r.name) as roles
            FROM app_user u
            LEFT JOIN app_user_role ur ON u.user_id = ur.user_id
            LEFT JOIN app_role r ON ur.role_id = r.role_id
            GROUP BY u.user_id, u.email, u.full_name, u.is_active, u.created_at
            ORDER BY u.created_at;
        """)
        
        users = cur.fetchall()
        
        if not users:
            logger.info("No users found in database.")
        else:
            for user in users:
                status = "ACTIVE" if user['is_active'] else "INACTIVE"
                roles = ', '.join(user['roles']) if user['roles'][0] else "No roles"
                logger.info(f"")
                logger.info(f"User ID: {user['user_id']}")
                logger.info(f"Email: {user['email']}")
                logger.info(f"Full Name: {user['full_name']}")
                logger.info(f"Status: {status}")
                logger.info(f"Roles: {roles}")
                logger.info(f"Created: {user['created_at']}")
                logger.info(f"{'-' * 60}")
        
        # Get role statistics
        cur.execute("SELECT name, COUNT(*) as user_count FROM app_role r LEFT JOIN app_user_role ur ON r.role_id = ur.role_id GROUP BY r.role_id, r.name;")
        role_stats = cur.fetchall()
        
        logger.info("")
        logger.info("=== ROLE STATISTICS ===")
        for stat in role_stats:
            logger.info(f"{stat['name']}: {stat['user_count']} users")
        
        cur.close()
        
    except Exception as error:
        logger.error(f"ERROR: {error}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    read_users()
