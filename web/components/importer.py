"""
Web Import Wrapper Module
Version: 1.61

Provides safe wrapper functions for UI to import platform and customer requirements.
All DB writes are delegated to import_platform and import_customer modules.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'import'))
from import_platform import load_platform_csv, load_platform_jsonl
from import_customer import load_customer_csv, load_customer_jsonl


def import_platform_file(uploaded_file_bytes: bytes, filetype: str) -> dict:
    """
    Import platform requirements from uploaded file.

    Args:
        uploaded_file_bytes: Raw bytes of the uploaded file
        filetype: 'csv' or 'jsonl'

    Returns:
        dict with 'inserted', 'failed' counts and 'status' message
    """
    suffix = f".{filetype}"

    with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded_file_bytes)
        tmp_path = tmp.name

    try:
        if filetype == 'csv':
            result = load_platform_csv(tmp_path)
        elif filetype == 'jsonl':
            result = load_platform_jsonl(tmp_path)
        else:
            return {"inserted": 0, "failed": 0, "status": f"Unsupported filetype: {filetype}"}

        result["status"] = "success"
        return result
    except Exception as e:
        return {"inserted": 0, "failed": 0, "status": f"Error: {str(e)}"}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def import_customer_file(customer_id: str, uploaded_file_bytes: bytes, filetype: str) -> dict:
    """
    Import customer requirements from uploaded file.

    Args:
        customer_id: Customer identifier
        uploaded_file_bytes: Raw bytes of the uploaded file
        filetype: 'csv' or 'jsonl'

    Returns:
        dict with 'inserted', 'failed' counts and 'status' message
    """
    suffix = f".{filetype}"

    with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded_file_bytes)
        tmp_path = tmp.name

    try:
        if filetype == 'csv':
            result = load_customer_csv(customer_id, tmp_path)
        elif filetype == 'jsonl':
            result = load_customer_jsonl(customer_id, tmp_path)
        else:
            return {"inserted": 0, "failed": 0, "status": f"Unsupported filetype: {filetype}"}

        result["status"] = "success"
        return result
    except Exception as e:
        return {"inserted": 0, "failed": 0, "status": f"Error: {str(e)}"}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
