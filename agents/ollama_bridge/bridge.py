from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)
CORS(app)

# Databázové připojení (přebírá se z .env souboru přes GitHub Action)
def get_db_engine():
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    return create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

engine = get_db_engine()

@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({"version": "1.0.0-ollama", "status": "running"}), 200

@app.route('/system-status', methods=['POST'])
def receive_telemetry():
    """
    Endpoint pro příjem dat z resource_monitor.py
    """
    data = request.get_json(silent=True)
    if not data:
        return "No data received", 400
        
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO system_telemetry_v1 
                    (node_name, cpu_usage, ram_usage, disk_free_gb, last_update) 
                    VALUES (:node, :cpu, :ram, :disk, CURRENT_TIMESTAMP) 
                    ON CONFLICT (node_name) 
                    DO UPDATE SET 
                        cpu_usage = :cpu, 
                        ram_usage = :ram, 
                        disk_free_gb = :disk, 
                        last_update = CURRENT_TIMESTAMP
                """), 
                {
                    "node": data.get('node'), 
                    "cpu": data.get('cpu'), 
                    "ram": data.get('ram'), 
                    "disk": data.get('disk')
                }
            )
            conn.commit()
        return "OK", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Ollama Bridge API v1.0.0")
    print("Starting on http://0.0.0.0:5002")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002)