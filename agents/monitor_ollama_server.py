#!/usr/bin/env python3
"""
Agent: monitor_ollama_server
Version: 1.6
Description: Monitors Ollama LLM server health and reports heartbeat with CPU/RAM metrics
"""

import os
import sys
import time
import requests
import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.db_bridge.database import update_agent_heartbeat

AGENT_NAME = "monitor_ollama_server"


def get_resource_metrics():
    """Get current CPU and RAM usage."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2)
    }


def check_ollama_health():
    """Check Ollama server health and return metrics."""
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_version = os.getenv('OLLAMA_MOD_VERSION', 'v0.5')

    try:
        # Check if Ollama is responding
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)

        if response.status_code == 200:
            models = response.json().get('models', [])
            model_count = len(models)

            return {
                "status": "active",
                "module_version": ollama_version,
                "mode": "active",
                "ollama_url": ollama_url,
                "models_available": model_count,
                "models": [m.get('name', 'unknown') for m in models[:5]]
            }
        else:
            return {
                "status": "error",
                "module_version": ollama_version,
                "mode": "offline",
                "error": f"HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "module_version": ollama_version,
            "mode": "offline",
            "error": "Connection timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline",
            "module_version": ollama_version,
            "mode": "offline",
            "error": "Cannot connect to Ollama server"
        }
    except Exception as e:
        return {
            "status": "error",
            "module_version": ollama_version,
            "mode": "offline",
            "error": str(e)
        }


def main():
    """Main monitoring loop."""
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_version = os.getenv('OLLAMA_MOD_VERSION', 'v0.5')

    print(f"[{AGENT_NAME}] Starting Ollama monitoring agent...")
    print(f"[{AGENT_NAME}] Ollama URL: {ollama_url}")
    print(f"[{AGENT_NAME}] Module Version: {ollama_version}")

    while True:
        try:
            health = check_ollama_health()
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

            print(f"[{AGENT_NAME}] Heartbeat sent: {health.get('status')} | Mode: {health.get('mode')} | CPU={metrics['cpu_percent']}%")

        except Exception as e:
            print(f"[{AGENT_NAME}] Error: {e}")
            try:
                update_agent_heartbeat(
                    agent_name=AGENT_NAME,
                    queue_size=0,
                    details={
                        "status": "error",
                        "module_version": os.getenv('OLLAMA_MOD_VERSION', 'v0.5'),
                        "mode": "offline",
                        "error": str(e)
                    }
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
