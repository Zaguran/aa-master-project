"""
Traceability Component
Version: 1.66
Task: H.1 - Trace Engine + Coverage Classification + Graphviz generator

Provides trace retrieval and SVG generation for traceability visualization.
"""

import os
import sys
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.trace.trace_engine import build_trace_for_requirements, generate_trace_graph


def get_trace(req_id: str, platform_req_id: str) -> dict:
    """
    Get traceability structure for a customer requirement and its matched platform requirement.

    Args:
        req_id: Customer requirement ID (from attributes.req_id)
        platform_req_id: Platform requirement ID (from attributes.req_id)

    Returns:
        dict with:
        {
            "customer_req": {...},
            "platform_req": {...},
            "system_nodes": [...],
            "architecture_nodes": [...],
            "code_nodes": [...],
            "test_nodes": [...],
        }
    """
    return build_trace_for_requirements(req_id, platform_req_id)


def generate_svg(trace_dict: dict, output_path: str, coverage_color: str = "GRAY") -> str:
    """
    Generate SVG visualization from trace structure.

    1. Writes DOT file using trace_agent.generate_trace_graph()
    2. Calls Graphviz using subprocess: dot -Tsvg trace.dot -o trace.svg
    3. Returns SVG file path

    Args:
        trace_dict: Trace structure from get_trace()
        output_path: Output path for SVG file (without extension)
        coverage_color: Color for main nodes ("GREEN", "YELLOW", "RED", "GRAY")

    Returns:
        Path to generated SVG file, or error message if generation fails
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Generate DOT file
        dot_path = generate_trace_graph(trace_dict, output_path, coverage_color)

        # Determine SVG output path
        svg_path = output_path if output_path.endswith(".svg") else f"{output_path}.svg"

        # Call Graphviz to render SVG
        result = subprocess.run(
            ["dot", "-Tsvg", dot_path, "-o", svg_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown Graphviz error"
            print(f"Graphviz error: {error_msg}")
            return f"Error: {error_msg}"

        return svg_path

    except FileNotFoundError:
        error_msg = "Graphviz 'dot' command not found. Please install Graphviz."
        print(error_msg)
        return f"Error: {error_msg}"
    except subprocess.TimeoutExpired:
        error_msg = "Graphviz rendering timed out"
        print(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating SVG: {error_msg}")
        return f"Error: {error_msg}"


def generate_dot_only(trace_dict: dict, output_path: str, coverage_color: str = "GRAY") -> str:
    """
    Generate only DOT file (without SVG rendering).
    Useful when Graphviz is not available.

    Args:
        trace_dict: Trace structure from get_trace()
        output_path: Output path for DOT file
        coverage_color: Color for main nodes

    Returns:
        Path to generated DOT file
    """
    return generate_trace_graph(trace_dict, output_path, coverage_color)


def read_svg_content(svg_path: str) -> str:
    """
    Read SVG file content for embedding in web page.

    Args:
        svg_path: Path to SVG file

    Returns:
        SVG content as string, or empty string if file not found
    """
    try:
        if os.path.exists(svg_path):
            with open(svg_path, "r") as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"Error reading SVG: {e}")
        return ""
