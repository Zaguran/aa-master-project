import psutil
import requests
import time

# Správná konfigurace pro Ollama VM
NODE_NAME = "Hetzner-Ollama-02"

BRIDGE_URL = "http://128.140.108.240:5002/system-status"

def collect_and_send():
    stats = {
        "node": NODE_NAME,
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": round(psutil.disk_usage('/').free / (1024**3), 2)
    }
    try:
        # Přidán timeout, aby monitor nezamrzl při výpadku sítě
        response = requests.post(BRIDGE_URL, json=stats, timeout=5)
        print(f"[{time.strftime('%H:%M:%S')}] Status: {response.status_code}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Chyba spojení: {e}")

if __name__ == "__main__":
    print(f"Startuji monitoring pro {NODE_NAME}...")
    while True:
        collect_and_send()
        time.sleep(60)