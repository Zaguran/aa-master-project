from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Načtení proměnných z .env (pro databázi, pokud ji používáš)
load_dotenv()

app = Flask(__name__)

# Úložiště pro data z monitoru (v paměti)
system_stats = {}

@app.route('/api/version', methods=['GET'])
def get_version():
    """Základní test funkčnosti Bridge"""
    return jsonify({
        "status": "running",
        "version": "1.0.0-ollama",
        "node": "Hetzner-OL-02"
    })

@app.route('/system-status', methods=['POST'])
def update_status():
    """Endpoint pro příjem dat z resource_monitor.py"""
    global system_stats
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    node_name = data.get("node", "unknown")
    system_stats[node_name] = {
        "cpu": data.get("cpu"),
        "ram": data.get("ram"),
        "disk": data.get("disk"),
        "last_update": data.get("timestamp")
    }
    
    print(f"Příjata data z uzlu: {node_name}")
    return jsonify({"status": "success"}), 200

@app.route('/system-status', methods=['GET'])
def get_status():
    """Zobrazení aktuálních posbíraných dat"""
    return jsonify(system_stats)

if __name__ == '__main__':
    # Port 5002 podle tvé konfigurace
    app.run(host='0.0.0.0', port=5002)