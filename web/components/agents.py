import sys
import os

# Fix Python path for Docker/Linux compatibility
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.db_bridge.database import list_agent_status


def get_agent_overview():
    """Get overview of all agents from agent_status table."""
    data = list_agent_status()
    return [
        {
            "agent": row["agent_name"],
            "status": row["status"],
            "last_heartbeat": row["last_heartbeat"],
            "queue": row["queue_size"],
            "details": row["details"],
        }
        for row in data
    ]
