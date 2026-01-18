import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import json

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT'),
        options="-c search_path=work_aa"
    )

def get_aa_stats():
    """Vrací statistiky tabulek pro Dashboard"""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        tables = ['projects', 'nodes', 'links', 'customer']
        stats = []
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()['count']
            stats.append({"Tabulka": table, "Počet záznamů": count})
        cur.close()
        conn.close()
        return stats
    except Exception as e:
        print(f"Chyba DB: {e}")
        return []

def get_table_data(table_name, limit=20, offset=0):
    """Vrací data konkrétní tabulky pro Table View"""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cur.fetchone()['count']
        cur.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows, total
    except Exception as e:
        return str(e), 0

def update_agent_heartbeat(agent_name: str, queue_size: int = 0, details: dict = None):
    """Update agent heartbeat in agent_status table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if details is None:
            details = {}
        
        cur.execute("""
            UPDATE agent_status
            SET last_heartbeat = now(),
                queue_size = %s,
                details = %s
            WHERE agent_name = %s
        """, (queue_size, json.dumps(details), agent_name))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error updating heartbeat for {agent_name}: {e}")

def list_agent_status():
    """List all agent status records."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT agent_name, status, last_heartbeat, queue_size, details
            FROM agent_status
            ORDER BY agent_name
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing agent status: {e}")
        return []

def insert_or_update_platform_requirement(req: dict):
    """
    Insert or update platform requirement in nodes table.
    Expected keys: req_id, text, type, priority, asil, owner, version, baseline, status
    Optional keys: id_type (defaults to 'requirement')
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        id_type = req.get("id_type", "requirement")

        attributes = {
            "req_id": req.get("req_id"),
            "type": req.get("type"),
            "priority": req.get("priority"),
            "owner": req.get("owner"),
            "baseline": req.get("baseline")
        }

        # Check if exists
        cur.execute("""
            SELECT node_uuid FROM nodes
            WHERE project_id = 'Platform_A'
              AND scope = 'platform'
              AND attributes->>'req_id' = %s
        """, (req.get("req_id"),))

        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE nodes SET
                    content = %s,
                    asil = %s,
                    version = %s,
                    node_status = %s,
                    attributes = %s,
                    id_type = %s
                WHERE node_uuid = %s
            """, (
                req.get("text"),
                req.get("asil"),
                req.get("version"),
                req.get("status"),
                json.dumps(attributes),
                id_type,
                existing["node_uuid"]
            ))
        else:
            cur.execute("""
                INSERT INTO nodes (project_id, type, scope, content, asil, version, node_status, attributes, id_type)
                VALUES ('Platform_A', 'requirement', 'platform', %s, %s, %s, %s, %s, %s)
            """, (
                req.get("text"),
                req.get("asil"),
                req.get("version"),
                req.get("status"),
                json.dumps(attributes),
                id_type
            ))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error inserting/updating platform requirement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def insert_or_update_customer_requirement(customer_id: str, req: dict):
    """
    Insert or update customer requirement in nodes table.
    Expected keys: req_id, text, priority, source_doc
    Optional keys: id_type (defaults to 'requirement')
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        project_id = f"Customer_{customer_id}"
        id_type = req.get("id_type", "requirement")

        attributes = {
            "req_id": req.get("req_id"),
            "priority": req.get("priority"),
            "source_doc": req.get("source_doc")
        }

        cur.execute("""
            SELECT node_uuid FROM nodes
            WHERE project_id = %s
              AND scope = 'customer'
              AND attributes->>'req_id' = %s
        """, (project_id, req.get("req_id")))

        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE nodes SET
                    content = %s,
                    attributes = %s,
                    id_type = %s
                WHERE node_uuid = %s
            """, (
                req.get("text"),
                json.dumps(attributes),
                id_type,
                existing["node_uuid"]
            ))
        else:
            cur.execute("""
                INSERT INTO nodes (project_id, type, scope, content, attributes, id_type)
                VALUES (%s, 'requirement', 'customer', %s, %s, %s)
            """, (
                project_id,
                req.get("text"),
                json.dumps(attributes),
                id_type
            ))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error inserting/updating customer requirement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def create_customer_project(customer_id: str):
    """Create customer project in projects table."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        project_id = f"Customer_{customer_id}"

        cur.execute("""
            INSERT INTO projects (project_id, type, status)
            VALUES (%s, 'CUSTOMER', 'ACTIVE')
            ON CONFLICT (project_id) DO NOTHING
        """, (project_id,))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error creating customer project: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def list_projects():
    """List all projects ordered by project_id."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM projects ORDER BY project_id")
        rows = cur.fetchall()

        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing projects: {e}")
        return []

def agent_loop():
    """Tato funkce bude srdcem asynchronního agenta."""
    print("DB Bridge Agent startuje...")
    while True:
        try:
            # Zde bude později logika pro zpracování úkolů
            pass
        except Exception as e:
            print(f"Chyba agenta: {e}")
        time.sleep(30)

# ============================================================================
# USER MANAGEMENT FUNCTIONS (v1.64)
# ============================================================================

def list_all_users() -> list:
    """Return all users with their roles."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                u.user_id,
                u.email,
                u.full_name,
                u.is_active,
                u.created_at,
                COALESCE(ARRAY_AGG(r.name) FILTER (WHERE r.name IS NOT NULL), ARRAY[]::text[]) as roles
            FROM app_user u
            LEFT JOIN app_user_role ur ON u.user_id = ur.user_id
            LEFT JOIN app_role r ON ur.role_id = r.role_id
            GROUP BY u.user_id, u.email, u.full_name, u.is_active, u.created_at
            ORDER BY u.created_at DESC
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing users: {e}")
        return []


def create_user(email: str, full_name: str, password_hash: str, initial_role: str = "visitor") -> dict:
    """Create new user and assign initial role."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if user already exists
        cur.execute("SELECT user_id FROM app_user WHERE email = %s", (email,))
        if cur.fetchone():
            return {"status": "error", "message": "User with this email already exists"}

        # Insert user
        cur.execute("""
            INSERT INTO app_user (email, full_name, password_hash, is_active)
            VALUES (%s, %s, %s, TRUE)
            RETURNING user_id
        """, (email, full_name, password_hash))

        user = cur.fetchone()
        user_id = user['user_id']

        # Get role_id for initial_role
        cur.execute("SELECT role_id FROM app_role WHERE name = %s", (initial_role,))
        role = cur.fetchone()

        if role:
            cur.execute("""
                INSERT INTO app_user_role (user_id, role_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (user_id, role['role_id']))

        conn.commit()
        cur.close()
        return {"status": "success", "user_id": str(user_id)}
    except Exception as e:
        print(f"Error creating user: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


def assign_role_to_user(user_id: str, role_name: str) -> bool:
    """Assign role to user."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get role_id
        cur.execute("SELECT role_id FROM app_role WHERE name = %s", (role_name,))
        role = cur.fetchone()

        if not role:
            return False

        cur.execute("""
            INSERT INTO app_user_role (user_id, role_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user_id, role['role_id']))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error assigning role: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def remove_role_from_user(user_id: str, role_name: str) -> bool:
    """Remove role from user."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get role_id
        cur.execute("SELECT role_id FROM app_role WHERE name = %s", (role_name,))
        role = cur.fetchone()

        if not role:
            return False

        cur.execute("""
            DELETE FROM app_user_role
            WHERE user_id = %s AND role_id = %s
        """, (user_id, role['role_id']))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error removing role: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def deactivate_user(user_id: str) -> bool:
    """Set is_active = FALSE for user."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE app_user SET is_active = FALSE WHERE user_id = %s
        """, (user_id,))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def activate_user(user_id: str) -> bool:
    """Set is_active = TRUE for user."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE app_user SET is_active = TRUE WHERE user_id = %s
        """, (user_id,))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error activating user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_available_roles() -> list:
    """Get list of all roles."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT role_id, name FROM app_role ORDER BY name")
        rows = cur.fetchall()

        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error getting roles: {e}")
        return []


# ============================================================================
# CUSTOMER MANAGEMENT FUNCTIONS (v1.64)
# ============================================================================

def list_customers() -> list:
    """Return all customers from projects table where type='CUSTOMER'."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                project_id as customer_id,
                project_id as name,
                type,
                status,
                customer_id as linked_customer,
                created_at
            FROM projects
            WHERE type = 'CUSTOMER'
            ORDER BY project_id
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing customers: {e}")
        return []


def create_customer(customer_id: str, name: str, description: str = "", industry: str = "") -> dict:
    """Create new customer project."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        project_id = customer_id if customer_id.startswith("Customer_") else f"Customer_{customer_id}"

        # Check if customer already exists
        cur.execute("SELECT project_id FROM projects WHERE project_id = %s", (project_id,))
        if cur.fetchone():
            return {"status": "error", "message": "Customer with this ID already exists"}

        cur.execute("""
            INSERT INTO projects (project_id, type, status)
            VALUES (%s, 'CUSTOMER', 'ACTIVE')
        """, (project_id,))

        conn.commit()
        cur.close()
        return {"status": "success", "customer_id": project_id}
    except Exception as e:
        print(f"Error creating customer: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


def update_customer(customer_id: str, status: str = None) -> bool:
    """Update customer status."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        if status:
            cur.execute("""
                UPDATE projects SET status = %s WHERE project_id = %s AND type = 'CUSTOMER'
            """, (status, customer_id))

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error updating customer: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete_customer(customer_id: str) -> dict:
    """Delete customer (check for nodes first)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check for associated nodes
        cur.execute("SELECT COUNT(*) as count FROM nodes WHERE project_id = %s", (customer_id,))
        count = cur.fetchone()['count']

        if count > 0:
            return {"status": "error", "message": f"Cannot delete: {count} requirements linked to this customer"}

        cur.execute("DELETE FROM projects WHERE project_id = %s AND type = 'CUSTOMER'", (customer_id,))

        conn.commit()
        cur.close()
        return {"status": "success"}
    except Exception as e:
        print(f"Error deleting customer: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


# ============================================================================
# PLATFORM MANAGEMENT FUNCTIONS (v1.64)
# ============================================================================

def list_platforms() -> list:
    """Return all platforms from projects table where type='PLATFORM'."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                project_id as platform_id,
                project_id as name,
                type,
                status,
                baseline_version as version,
                created_at
            FROM projects
            WHERE type = 'PLATFORM'
            ORDER BY project_id
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error listing platforms: {e}")
        return []


def create_platform(platform_id: str, name: str, version: str = "1.0", status: str = "Active", config: dict = None) -> dict:
    """Create new platform project."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        project_id = platform_id if platform_id.startswith("Platform_") else f"Platform_{platform_id}"

        # Check if platform already exists
        cur.execute("SELECT project_id FROM projects WHERE project_id = %s", (project_id,))
        if cur.fetchone():
            return {"status": "error", "message": "Platform with this ID already exists"}

        # Map status to uppercase
        status_map = {"Active": "ACTIVE", "Development": "DEVELOPMENT", "Archived": "ARCHIVED"}
        db_status = status_map.get(status, "ACTIVE")

        cur.execute("""
            INSERT INTO projects (project_id, type, status, baseline_version)
            VALUES (%s, 'PLATFORM', %s, %s)
        """, (project_id, db_status, version))

        conn.commit()
        cur.close()
        return {"status": "success", "platform_id": project_id}
    except Exception as e:
        print(f"Error creating platform: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


def update_platform(platform_id: str, status: str = None, version: str = None) -> bool:
    """Update platform details."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        updates = []
        params = []

        if status:
            status_map = {"Active": "ACTIVE", "Development": "DEVELOPMENT", "Archived": "ARCHIVED"}
            db_status = status_map.get(status, status)
            updates.append("status = %s")
            params.append(db_status)

        if version:
            updates.append("baseline_version = %s")
            params.append(version)

        if updates:
            params.append(platform_id)
            query = f"UPDATE projects SET {', '.join(updates)} WHERE project_id = %s AND type = 'PLATFORM'"
            cur.execute(query, params)

        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error updating platform: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete_platform(platform_id: str) -> dict:
    """Delete platform (check for nodes first)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check for associated nodes
        cur.execute("SELECT COUNT(*) as count FROM nodes WHERE project_id = %s", (platform_id,))
        count = cur.fetchone()['count']

        if count > 0:
            return {"status": "error", "message": f"Cannot delete: {count} requirements linked to this platform"}

        cur.execute("DELETE FROM projects WHERE project_id = %s AND type = 'PLATFORM'", (platform_id,))

        conn.commit()
        cur.close()
        return {"status": "success"}
    except Exception as e:
        print(f"Error deleting platform: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


# ============================================================================
# COVERAGE CLASSIFICATION FUNCTIONS (v1.66 - Task H.1)
# ============================================================================

# Coverage thresholds
FULL_MATCH_THRESHOLD = 0.85
PARTIAL_MATCH_THRESHOLD = 0.65


def list_best_matches(model_id: int, rfq_id: str, platform_id: str) -> list:
    """
    Get best match for each customer requirement.
    Returns the highest-ranked match (rank=1) per customer_req_id.

    Args:
        model_id: The embedding model ID used for matching
        rfq_id: The RFQ/customer project ID
        platform_id: The platform project ID

    Returns:
        List of dicts with customer_req_id, platform_req_id, cosine_similarity
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT DISTINCT ON (customer_req_id)
                customer_req_id,
                platform_req_id,
                cosine_similarity
            FROM req_match
            WHERE model_id = %s
              AND rfq_id = %s
              AND platform_id = %s
            ORDER BY customer_req_id, rank ASC
        """, (model_id, rfq_id, platform_id))

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error listing best matches: {e}")
        return []


def classify_coverage(full_th: float, partial_th: float, rows: list) -> list:
    """
    Classify coverage for each match row based on cosine similarity thresholds.

    Args:
        full_th: Threshold for GREEN (full match), e.g. 0.85
        partial_th: Threshold for YELLOW (partial match), e.g. 0.65
        rows: List of dicts with cosine_similarity key

    Returns:
        List of dicts with added 'color' field:
        {
            "customer_req_id": ...,
            "platform_req_id": ...,
            "similarity": ...,
            "color": "GREEN" | "YELLOW" | "RED"
        }
    """
    result = []
    for row in rows:
        similarity = row.get("cosine_similarity", 0.0)
        if similarity is None:
            similarity = 0.0

        if similarity >= full_th:
            color = "GREEN"
        elif similarity >= partial_th:
            color = "YELLOW"
        else:
            color = "RED"

        result.append({
            "customer_req_id": row.get("customer_req_id"),
            "platform_req_id": row.get("platform_req_id"),
            "similarity": similarity,
            "color": color
        })

    return result


# ============================================================================
# EMBEDDING FUNCTIONS (v1.70 - Task F)
# ============================================================================

def get_or_create_embedding_model(model_name: str, vector_dims: int = 768, framework: str = 'ollama') -> int:
    """
    Get or create embedding model registry entry.

    Returns:
        model_id (int)
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Try to get existing
        cur.execute("""
            SELECT model_id FROM embedding_models
            WHERE model_name = %s
        """, (model_name,))

        row = cur.fetchone()
        if row:
            model_id = row[0]
        else:
            # Create new
            cur.execute("""
                INSERT INTO embedding_models (model_name, vector_dims, framework)
                VALUES (%s, %s, %s)
                RETURNING model_id
            """, (model_name, vector_dims, framework))
            model_id = cur.fetchone()[0]
            conn.commit()

        cur.close()
        return model_id

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error managing embedding model: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_nodes_for_embedding(scope: str = None, only_missing: bool = True, model_id: int = None, limit: int = None) -> list:
    """
    Get nodes that need embeddings.

    Args:
        scope: 'customer', 'platform', or None (all)
        only_missing: If True, skip nodes that already have embeddings
        model_id: Model ID to check for existing embeddings
        limit: Maximum number of nodes to return

    Returns:
        List of node dicts
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT n.node_uuid, n.project_id, n.node_id, n.type, n.scope,
                   n.content, n.attributes
        """
        # Add node_id from attributes if available
        query += """
            FROM nodes n
            WHERE n.type = 'requirement'
              AND n.content IS NOT NULL
              AND n.content <> ''
        """

        params = []

        if scope:
            query += " AND n.scope = %s"
            params.append(scope)

        if only_missing and model_id:
            query += """
                AND NOT EXISTS (
                    SELECT 1 FROM embeddings e
                    WHERE e.node_uuid = n.node_uuid
                      AND e.model_id = %s
                )
            """
            params.append(model_id)

        query += " ORDER BY n.created_at"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cur.execute(query, params)
        nodes = cur.fetchall()
        cur.close()
        conn.close()

        # Extract node_id from attributes if present
        result = []
        for n in nodes:
            node_dict = dict(n)
            if node_dict.get('attributes') and isinstance(node_dict['attributes'], dict):
                node_dict['node_id'] = node_dict['attributes'].get('req_id', str(node_dict['node_uuid'])[:8])
            else:
                node_dict['node_id'] = str(node_dict['node_uuid'])[:8]
            result.append(node_dict)

        return result

    except Exception as e:
        print(f"Error getting nodes for embedding: {e}")
        return []


def insert_embedding(node_uuid: str, model_id: int, content_hash: str, embedding_vector: list) -> bool:
    """
    Insert embedding for a node.

    Args:
        node_uuid: Node UUID
        model_id: Model ID
        content_hash: SHA256 hash of content
        embedding_vector: List of floats (vector)

    Returns:
        True if successful
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Convert list to pgvector format
        vector_str = '[' + ','.join(map(str, embedding_vector)) + ']'

        cur.execute("""
            INSERT INTO embeddings (node_uuid, model_id, content_hash, embedding)
            VALUES (%s, %s, %s, %s::vector)
            ON CONFLICT (node_uuid, model_id, content_hash) DO NOTHING
        """, (node_uuid, model_id, content_hash, vector_str))

        conn.commit()
        cur.close()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error inserting embedding: {e}")
        return False
    finally:
        if conn:
            conn.close()


# ============================================================================
# MATCHING FUNCTIONS (v1.70 - Task G)
# ============================================================================

def get_embeddings_by_scope(model_id: int, scope: str) -> list:
    """
    Get all embeddings for nodes with given scope.

    Args:
        model_id: Model ID
        scope: 'customer' or 'platform'

    Returns:
        List of dicts with node_uuid, node_id, content, embedding
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT n.node_uuid, n.attributes->>'req_id' as node_id, n.content, e.embedding
            FROM embeddings e
            JOIN nodes n ON e.node_uuid = n.node_uuid
            WHERE e.model_id = %s AND n.scope = %s
        """, (model_id, scope))

        results = cur.fetchall()
        cur.close()
        conn.close()

        return [dict(r) for r in results] if results else []

    except Exception as e:
        print(f"Error getting embeddings: {e}")
        return []


def insert_match(model_id: int, customer_uuid: str, platform_uuid: str,
                similarity: float, rank: int, classification: str) -> bool:
    """
    Insert matching result.

    Args:
        model_id: Model ID
        customer_uuid: Customer node UUID
        platform_uuid: Platform node UUID
        similarity: Cosine similarity score
        rank: Match rank (1 = best match)
        classification: 'GREEN', 'YELLOW', or 'RED'

    Returns:
        True if successful
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO matches
            (model_id, customer_node_uuid, platform_node_uuid,
             similarity_score, match_rank, classification)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (model_id, customer_uuid, platform_uuid, similarity, rank, classification))

        conn.commit()
        cur.close()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error inserting match: {e}")
        return False
    finally:
        if conn:
            conn.close()


def clear_matches(model_id: int) -> bool:
    """Delete all matches for given model."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM matches WHERE model_id = %s", (model_id,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error clearing matches: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_match_statistics(model_id: int = 1) -> dict:
    """
    Get match statistics for a model.

    Args:
        model_id: Embedding model ID

    Returns:
        Dict with GREEN, YELLOW, RED counts and percentages
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Count by classification (rank 1 only = best match per customer)
        cur.execute("""
            SELECT classification, COUNT(*) as count
            FROM matches
            WHERE model_id = %s AND match_rank = 1
            GROUP BY classification
        """, (model_id,))

        results = cur.fetchall()
        cur.close()
        conn.close()

        counts = {'GREEN': 0, 'YELLOW': 0, 'RED': 0}
        for row in results:
            if row['classification'] in counts:
                counts[row['classification']] = row['count']

        total = sum(counts.values())

        if total == 0:
            return {
                'total': 0,
                'green': 0,
                'yellow': 0,
                'red': 0,
                'pct_green': 0,
                'pct_yellow': 0,
                'pct_red': 0
            }

        return {
            'total': total,
            'green': counts['GREEN'],
            'yellow': counts['YELLOW'],
            'red': counts['RED'],
            'pct_green': round(counts['GREEN'] / total * 100, 1),
            'pct_yellow': round(counts['YELLOW'] / total * 100, 1),
            'pct_red': round(counts['RED'] / total * 100, 1)
        }

    except Exception as e:
        print(f"Error getting match statistics: {e}")
        return {'total': 0, 'green': 0, 'yellow': 0, 'red': 0}


if __name__ == "__main__":
    agent_loop()