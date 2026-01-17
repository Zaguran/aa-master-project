"""
Customer Requirements Import Module
Version: 1.61

Loads customer requirements from CSV or JSONL files into the database.
Does NOT create embeddings or call Ollama - strictly a database loader.
"""

import csv
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'db_bridge'))
from database import insert_or_update_customer_requirement, create_customer_project


def load_customer_csv(customer_id: str, path: str) -> dict:
    """
    Load customer requirements from CSV file.
    Expected columns: req_id, text, priority, source_doc
    Returns: dict with 'inserted' and 'failed' counts
    """
    # First ensure customer project exists
    create_customer_project(customer_id)

    inserted = 0
    failed = 0

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = insert_or_update_customer_requirement(customer_id, row)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


def load_customer_jsonl(customer_id: str, path: str) -> dict:
    """
    Load customer requirements from JSONL file.
    Each line is a JSON object with keys: req_id, text, priority, source_doc
    Returns: dict with 'inserted' and 'failed' counts
    """
    # First ensure customer project exists
    create_customer_project(customer_id)

    inserted = 0
    failed = 0

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            result = insert_or_update_customer_requirement(customer_id, req)
            if result:
                inserted += 1
            else:
                failed += 1

    return {"inserted": inserted, "failed": failed}


if __name__ == "__main__":
    print("Customer import module. Use load_customer_csv() or load_customer_jsonl().")
