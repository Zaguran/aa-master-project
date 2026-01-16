import os
import sys
import time
import psycopg2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.db_bridge.database import update_agent_heartbeat


def get_db_connection():
    """Get database connection with schema isolation to work_aa."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT'),
        options="-c search_path=work_aa"
    )


def check_db_health():
    """Check database health and return metrics."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Simple health check - query execution time
        start_time = time.time()
        cur.execute("SELECT 1")
        cur.fetchone()
        query_time = time.time() - start_time
        
        # Get database size
        cur.execute("""
            SELECT pg_database_size(current_database()) as db_size
        """)
        db_size = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            "status": "healthy",
            "query_time_ms": round(query_time * 1000, 2),
            "db_size_mb": round(db_size / (1024 * 1024), 2)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    """Main monitoring loop."""
    agent_name = "monitor_db_server"
    print(f"[{agent_name}] Starting DB monitoring agent...")
    
    while True:
        try:
            health = check_db_health()
            
            # Update heartbeat with health details
            update_agent_heartbeat(
                agent_name=agent_name,
                queue_size=0,
                details=health
            )
            
            print(f"[{agent_name}] Heartbeat sent: {health}")
            
        except Exception as e:
            print(f"[{agent_name}] Error: {e}")
            try:
                update_agent_heartbeat(
                    agent_name=agent_name,
                    queue_size=0,
                    details={"status": "error", "error": str(e)}
                )
            except:
                pass
        
        # Sleep for 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    main()
