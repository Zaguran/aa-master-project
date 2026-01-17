"""
Platform Requirements Import Module
Version: 1.65

Loads platform requirements from CSV or JSONL files into the database.
Does NOT create embeddings or call Ollama - strictly a database loader.
Supports id_type attribute (requirement/information).
"""

import csv
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'db_bridge'))
from database import insert_or_update_platform_requirement


def load_platform_csv(path: str) -> dict:
    """
    Load platform requirements from CSV file.
    Expected columns: req_id, text, type, priority, asil, owner, version, baseline, status
    Optional columns: id_type (defaults to 'requirement')
    Returns: dict with 'inserted' and 'failed' counts
    """
    inserted = 0
    failed = 0

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            req = {
                'req_id': row.get('req_id', ''),
                'text': row.get('text', ''),
                'type': row.get('type', ''),
                'priority': row.get('priority', ''),
                'asil': row.get('asil', ''),
                'owner': row.get('owner', ''),
                'version': row.get('version', ''),
                'baseline': row.get('baseline', ''),
                'status': row.get('status', ''),
                'id_type': row.get('id_type', 'requirement')
            }
            result = insert_or_update_platform_requirement(req)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


def load_platform_jsonl(path: str) -> dict:
    """
    Load platform requirements from JSONL file.
    Each line is a JSON object with keys: req_id, text, type, priority, asil, owner, version, baseline, status
    Optional keys: id_type (defaults to 'requirement')
    Returns: dict with 'inserted' and 'failed' counts
    """
    inserted = 0
    failed = 0

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            if 'id_type' not in req:
                req['id_type'] = 'requirement'
            result = insert_or_update_platform_requirement(req)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


if __name__ == "__main__":
    print("Platform import module. Use load_platform_csv() or load_platform_jsonl().")
