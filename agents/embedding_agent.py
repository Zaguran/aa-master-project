#!/usr/bin/env python3
"""
Agent: embedding_agent
Version: 1.6
Description: Generates semantic embeddings for requirements using Ollama LLM
Status: Scaffold - waiting for implementation
"""

import os
import sys
import time
import psutil

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.db_bridge.database import update_agent_heartbeat

AGENT_NAME = "embedding_agent"


def get_resource_metrics():
    """Get current CPU and RAM usage."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2)
    }


def main_loop():
    """Main daemon loop - sends heartbeat every 30s."""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')

    print(f"[{AGENT_NAME}] Starting daemon loop...")
    print(f"[{AGENT_NAME}] Connected to DB at {db_host}:{db_port}")
    print(f"[{AGENT_NAME}] Status: Scaffold (waiting for implementation)")

    while True:
        try:
            metrics = get_resource_metrics()

            details = {
                "mode": "scaffold",
                "status": "waiting_for_implementation",
                "version": "1.6",
                "cpu_percent": metrics["cpu_percent"],
                "ram_percent": metrics["ram_percent"],
                "ram_mb": metrics["ram_mb"]
            }

            update_agent_heartbeat(
                agent_name=AGENT_NAME,
                queue_size=0,
                details=details
            )

            print(f"[{AGENT_NAME}] Heartbeat sent: CPU={metrics['cpu_percent']}%, RAM={metrics['ram_percent']}%")

        except Exception as e:
            print(f"[{AGENT_NAME}] Error: {e}")

        time.sleep(30)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print(f"[{AGENT_NAME}] Shutting down...")
