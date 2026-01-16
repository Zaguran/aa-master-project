import os
import sys
import time
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.db_bridge.database import update_agent_heartbeat


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
                "models": [m.get('name', 'unknown') for m in models[:5]]  # First 5 models
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
    agent_name = "monitor_ollama_server"
    print(f"[{agent_name}] Starting Ollama monitoring agent...")
    print(f"[{agent_name}] Ollama URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    print(f"[{agent_name}] Module Version: {os.getenv('OLLAMA_MOD_VERSION', 'v0.5')}")
    
    while True:
        try:
            health = check_ollama_health()
            
            # Update heartbeat with health details including v0.5 and mode
            update_agent_heartbeat(
                agent_name=agent_name,
                queue_size=0,
                details=health
            )
            
            print(f"[{agent_name}] Heartbeat sent: {health.get('status')} | Mode: {health.get('mode')} | Version: {health.get('module_version')}")
            
        except Exception as e:
            print(f"[{agent_name}] Error: {e}")
            try:
                update_agent_heartbeat(
                    agent_name=agent_name,
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
    main()
