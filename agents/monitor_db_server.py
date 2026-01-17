#!/usr/bin/env python3
"""
Agent: monitor_db_server
Version: 1.6
Description: Monitors database health and reports heartbeat with CPU/RAM metrics
"""

import os
import sys
import time
import psycopg2
import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.db_bridge.database import update_agent_heartbeat

AGENT_NAME = "monitor_db_server"


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


def get_resource_metrics():
    """Get current CPU and RAM usage."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2)
    }


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
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')

    print(f"[{AGENT_NAME}] Starting DB monitoring agent...")
    print(f"[{AGENT_NAME}] Connected to DB at {db_host}:{db_port}")

    while True:
        try:
            health = check_db_health()
            metrics = get_resource_metrics()

            # Merge health and resource metrics
            details = {
                **health,
                "cpu_percent": metrics["cpu_percent"],
                "ram_percent": metrics["ram_percent"],
                "ram_mb": metrics["ram_mb"],
                "version": "1.6"
            }

            # Update heartbeat with health details
            update_agent_heartbeat(
                agent_name=AGENT_NAME,
                queue_size=0,
                details=details
            )

            print(f"[{AGENT_NAME}] Heartbeat sent: {health['status']}, CPU={metrics['cpu_percent']}%, RAM={metrics['ram_percent']}%")

        except Exception as e:
            print(f"[{AGENT_NAME}] Error: {e}")
            try:
                update_agent_heartbeat(
                    agent_name=AGENT_NAME,
                    queue_size=0,
                    details={"status": "error", "error": str(e)}
                )
            except:
                pass

        # Sleep for 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[{AGENT_NAME}] Shutting down...")
