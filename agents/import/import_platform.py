"""
Platform Requirements Import Module
Version: 1.61

Loads platform requirements from CSV or JSONL files into the database.
Does NOT create embeddings or call Ollama - strictly a database loader.
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
    Returns: dict with 'inserted' and 'failed' counts
    """
    inserted = 0
    failed = 0

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = insert_or_update_platform_requirement(row)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


def load_platform_jsonl(path: str) -> dict:
    """
    Load platform requirements from JSONL file.
    Each line is a JSON object with keys: req_id, text, type, priority, asil, owner, version, baseline, status
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
            result = insert_or_update_platform_requirement(req)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


if __name__ == "__main__":
    print("Platform import module. Use load_platform_csv() or load_platform_jsonl().")
