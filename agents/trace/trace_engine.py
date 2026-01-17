#!/usr/bin/env python3
"""
Agent: trace_engine
Version: 1.66
Description: Builds traceability structures and generates Graphviz DOT files.
Task: H.1 - Trace Engine + Coverage Classification + Graphviz generator
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.db_bridge.database import get_connection
from psycopg2.extras import RealDictCursor


def build_trace_for_requirements(req_id: str, platform_req_id: str) -> dict:
    """
    Build traceability structure for a customer requirement matched to a platform requirement.

    Navigates through:
    - Customer requirement (customer scope)
    - Platform requirement (platform scope)
    - System-level nodes (scope='system')
    - Architecture nodes (scope='arch')
    - Code nodes (scope='code')
    - Test nodes (scope='test')

    Uses links table to navigate: source_uuid -> target_uuid

    Returns structure:
    {
      "customer_req": {...},
      "platform_req": {...},
      "system_nodes": [...],
      "architecture_nodes": [...],
      "code_nodes": [...],
      "test_nodes": [...],
    }
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        result = {
            "customer_req": None,
            "platform_req": None,
            "system_nodes": [],
            "architecture_nodes": [],
            "code_nodes": [],
            "test_nodes": [],
        }

        # Get customer requirement by req_id from attributes
        cur.execute("""
            SELECT node_uuid, project_id, type, scope, content, attributes, asil, version, node_status
            FROM nodes
            WHERE scope = 'customer' AND attributes->>'req_id' = %s
            LIMIT 1
        """, (req_id,))
        customer_req = cur.fetchone()
        if customer_req:
            result["customer_req"] = dict(customer_req)

        # Get platform requirement by req_id from attributes
        cur.execute("""
            SELECT node_uuid, project_id, type, scope, content, attributes, asil, version, node_status
            FROM nodes
            WHERE scope = 'platform' AND attributes->>'req_id' = %s
            LIMIT 1
        """, (platform_req_id,))
        platform_req = cur.fetchone()
        if platform_req:
            result["platform_req"] = dict(platform_req)
            platform_uuid = platform_req["node_uuid"]

            # Collect all linked nodes via BFS traversal
            visited = set()
            to_visit = [platform_uuid]

            while to_visit:
                current_uuid = to_visit.pop(0)
                if current_uuid in visited:
                    continue
                visited.add(current_uuid)

                # Find linked nodes (target_uuid from links where source_uuid = current)
                cur.execute("""
                    SELECT target_uuid FROM links WHERE source_uuid = %s
                """, (current_uuid,))
                linked = cur.fetchall()

                for link in linked:
                    target_uuid = link["target_uuid"]
                    if target_uuid and target_uuid not in visited:
                        to_visit.append(target_uuid)

            # Remove the platform_uuid from visited (already in platform_req)
            visited.discard(platform_uuid)

            # Fetch all linked nodes and categorize by scope
            if visited:
                cur.execute("""
                    SELECT node_uuid, project_id, type, scope, content, attributes, asil, version, node_status
                    FROM nodes
                    WHERE node_uuid = ANY(%s)
                """, (list(visited),))
                linked_nodes = cur.fetchall()

                for node in linked_nodes:
                    node_dict = dict(node)
                    scope = node_dict.get("scope", "")

                    if scope == "system":
                        result["system_nodes"].append(node_dict)
                    elif scope == "arch":
                        result["architecture_nodes"].append(node_dict)
                    elif scope == "code":
                        result["code_nodes"].append(node_dict)
                    elif scope == "test":
                        result["test_nodes"].append(node_dict)

        cur.close()
        return result

    except Exception as e:
        print(f"Error building trace: {e}")
        return {
            "customer_req": None,
            "platform_req": None,
            "system_nodes": [],
            "architecture_nodes": [],
            "code_nodes": [],
            "test_nodes": [],
            "error": str(e)
        }
    finally:
        if conn:
            conn.close()


def generate_trace_graph(trace_dict: dict, outfile: str, coverage_color: str = "GRAY") -> str:
    """
    Generate Graphviz DOT file from trace structure.

    Node shapes:
    - customer req = ellipse
    - platform req = box
    - system = box
    - architecture = diamond
    - code = note
    - test = hexagon

    Colors:
    - GREEN   #4CAF50
    - YELLOW  #FFC107
    - RED     #F44336
    - GRAY    #BDBDBD

    Returns path to generated DOT file.
    Note: Does NOT call external binaries - only writes DOT file.
    """
    colors = {
        "GREEN": "#4CAF50",
        "YELLOW": "#FFC107",
        "RED": "#F44336",
        "GRAY": "#BDBDBD"
    }

    node_color = colors.get(coverage_color.upper(), colors["GRAY"])

    dot_lines = [
        "digraph TraceGraph {",
        "    rankdir=TB;",
        "    node [fontname=\"Helvetica\", fontsize=10];",
        "    edge [fontname=\"Helvetica\", fontsize=8];",
        ""
    ]

    node_id_map = {}
    node_counter = [0]

    def get_node_id(prefix):
        node_counter[0] += 1
        return f"{prefix}_{node_counter[0]}"

    def escape_label(text):
        if not text:
            return "N/A"
        text = str(text)[:50]
        text = text.replace('"', '\\"').replace('\n', '\\n')
        return text

    # Customer requirement (ellipse)
    if trace_dict.get("customer_req"):
        req = trace_dict["customer_req"]
        node_id = get_node_id("cust")
        req_id = req.get("attributes", {}).get("req_id", "N/A") if isinstance(req.get("attributes"), dict) else "N/A"
        label = escape_label(f"Customer: {req_id}")
        dot_lines.append(f'    {node_id} [label="{label}", shape=ellipse, style=filled, fillcolor="{node_color}"];')
        node_id_map["customer_req"] = node_id

    # Platform requirement (box)
    if trace_dict.get("platform_req"):
        req = trace_dict["platform_req"]
        node_id = get_node_id("plat")
        req_id = req.get("attributes", {}).get("req_id", "N/A") if isinstance(req.get("attributes"), dict) else "N/A"
        label = escape_label(f"Platform: {req_id}")
        dot_lines.append(f'    {node_id} [label="{label}", shape=box, style=filled, fillcolor="{node_color}"];')
        node_id_map["platform_req"] = node_id

        # Edge from customer to platform
        if "customer_req" in node_id_map:
            dot_lines.append(f'    {node_id_map["customer_req"]} -> {node_id} [label="matches"];')

    # System nodes (box)
    system_ids = []
    for idx, node in enumerate(trace_dict.get("system_nodes", [])):
        node_id = get_node_id("sys")
        label = escape_label(node.get("content", "System Node")[:30])
        dot_lines.append(f'    {node_id} [label="{label}", shape=box, style=filled, fillcolor="#E3F2FD"];')
        system_ids.append(node_id)

        # Edge from platform to system
        if "platform_req" in node_id_map:
            dot_lines.append(f'    {node_id_map["platform_req"]} -> {node_id} [label="derives"];')

    # Architecture nodes (diamond)
    arch_ids = []
    for idx, node in enumerate(trace_dict.get("architecture_nodes", [])):
        node_id = get_node_id("arch")
        label = escape_label(node.get("content", "Arch Node")[:30])
        dot_lines.append(f'    {node_id} [label="{label}", shape=diamond, style=filled, fillcolor="#FFF3E0"];')
        arch_ids.append(node_id)

        # Edge from system to arch (connect to first system node if exists)
        if system_ids:
            dot_lines.append(f'    {system_ids[0]} -> {node_id} [label="realizes"];')
        elif "platform_req" in node_id_map:
            dot_lines.append(f'    {node_id_map["platform_req"]} -> {node_id} [label="realizes"];')

    # Code nodes (note shape)
    code_ids = []
    for idx, node in enumerate(trace_dict.get("code_nodes", [])):
        node_id = get_node_id("code")
        label = escape_label(node.get("content", "Code Node")[:30])
        dot_lines.append(f'    {node_id} [label="{label}", shape=note, style=filled, fillcolor="#E8F5E9"];')
        code_ids.append(node_id)

        # Edge from arch to code
        if arch_ids:
            dot_lines.append(f'    {arch_ids[0]} -> {node_id} [label="implements"];')
        elif system_ids:
            dot_lines.append(f'    {system_ids[0]} -> {node_id} [label="implements"];')

    # Test nodes (hexagon)
    for idx, node in enumerate(trace_dict.get("test_nodes", [])):
        node_id = get_node_id("test")
        label = escape_label(node.get("content", "Test Node")[:30])
        dot_lines.append(f'    {node_id} [label="{label}", shape=hexagon, style=filled, fillcolor="#FCE4EC"];')

        # Edge from code to test
        if code_ids:
            dot_lines.append(f'    {code_ids[0]} -> {node_id} [label="verifies"];')
        elif arch_ids:
            dot_lines.append(f'    {arch_ids[0]} -> {node_id} [label="verifies"];')
        elif system_ids:
            dot_lines.append(f'    {system_ids[0]} -> {node_id} [label="verifies"];')

    dot_lines.append("}")

    dot_content = "\n".join(dot_lines)

    # Write DOT file
    dot_path = outfile if outfile.endswith(".dot") else f"{outfile}.dot"
    with open(dot_path, "w") as f:
        f.write(dot_content)

    return dot_path


if __name__ == "__main__":
    # Example usage
    print("Trace Agent v1.66")
    print("Use build_trace_for_requirements(req_id, platform_req_id) to build trace")
    print("Use generate_trace_graph(trace_dict, outfile) to generate DOT file")
