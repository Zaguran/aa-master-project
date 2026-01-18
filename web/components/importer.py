"""
Web Import Wrapper Module
Version: 1.65

Provides safe wrapper functions for UI to import platform and customer requirements.
All DB writes are delegated to import_platform and import_customer modules.
Supports multiple data types: requirements, architecture, code, tests, links.
"""

import os
import sys
import tempfile
import importlib.util

# Add /app to path for Docker compatibility (PYTHONPATH=/app)
# In Docker: agents/ is at /app/agents/
# Locally: agents/ is at project_root/agents/
if "/app" not in sys.path:
    sys.path.insert(0, "/app")

# Also add project root for local development
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def _load_module_from_path(module_name: str, file_path: str):
    """Load a Python module from file path (handles 'import' folder name issue)."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Resolve path to agents/import directory
# Try Docker path first, then local path
_import_dir = "/app/agents/import"
if not os.path.exists(_import_dir):
    _import_dir = os.path.join(_project_root, "agents", "import")

# Load modules using importlib (avoids 'import' keyword conflict)
_platform_module = _load_module_from_path(
    "import_platform",
    os.path.join(_import_dir, "import_platform.py")
)
_customer_module = _load_module_from_path(
    "import_customer",
    os.path.join(_import_dir, "import_customer.py")
)

load_platform_csv = _platform_module.load_platform_csv
load_platform_jsonl = _platform_module.load_platform_jsonl
load_customer_csv = _customer_module.load_customer_csv
load_customer_jsonl = _customer_module.load_customer_jsonl


def import_platform_file(
    uploaded_file_bytes: bytes,
    filetype: str,
    platform_id: str = None,
    data_type: str = "system_requirements"
) -> dict:
    """
    Import platform data from uploaded file.

    Args:
        uploaded_file_bytes: Raw bytes of the uploaded file
        filetype: 'csv' or 'jsonl'
        platform_id: Platform identifier (e.g., 'Platform_A')
        data_type: Type of data being imported (V-Model aligned):
            Requirements & Architecture (Left Side):
            - 'system_requirements'
            - 'system_architecture'
            - 'software_requirements'
            - 'software_architecture'
            Testing (Right Side):
            - 'system_test'
            - 'system_integration_test'
            - 'software_test'
            - 'software_integration_test'
            Test Results:
            - 'system_test_result'
            - 'system_integration_test_result'
            - 'software_test_result'
            - 'software_integration_test_result'
            Traceability:
            - 'traceability_links'

    Returns:
        dict with 'inserted', 'failed' counts, 'status' message, and metadata
    """
    # V-Model data types
    vmodel_types = [
        # Requirements & Architecture
        "system_requirements", "system_architecture",
        "software_requirements", "software_architecture",
        # Testing
        "system_test", "system_integration_test",
        "software_test", "software_integration_test",
        # Test Results
        "system_test_result", "system_integration_test_result",
        "software_test_result", "software_integration_test_result",
        # Traceability
        "traceability_links"
    ]

    suffix = f".{filetype}"

    with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded_file_bytes)
        tmp_path = tmp.name

    try:
        # For now, all V-Model data types use platform requirements loader
        # TODO: Implement specific loaders for each V-Model data type (architecture, code, tests, etc.)
        if data_type in vmodel_types:
            # Use platform requirements loader as default
            if filetype == 'csv':
                result = load_platform_csv(tmp_path)
            elif filetype == 'jsonl':
                result = load_platform_jsonl(tmp_path)
            else:
                return {"inserted": 0, "failed": 0, "status": f"Unsupported filetype: {filetype}"}
            
            result["status"] = "success"
            result["platform_id"] = platform_id
            result["data_type"] = data_type
            return result
        else:
            return {"inserted": 0, "failed": 0, "status": f"Unknown data type: {data_type}"}
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
