"""
Coverage Classification Component
Version: 1.66
Task: H.1 - Trace Engine + Coverage Classification + Graphviz generator

Provides coverage summary computation for requirements matching.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.db_bridge.database import (
    list_best_matches,
    classify_coverage,
    FULL_MATCH_THRESHOLD,
    PARTIAL_MATCH_THRESHOLD
)


def compute_coverage_summary(model_id: int, rfq_id: str, platform_id: str) -> dict:
    """
    Compute coverage summary for a given model, RFQ, and platform.

    Uses list_best_matches() to get best match per customer requirement,
    then classify_coverage() to determine GREEN/YELLOW/RED status.

    Args:
        model_id: The embedding model ID
        rfq_id: The RFQ/customer project ID
        platform_id: The platform project ID

    Returns:
        dict with:
        {
            "total": total number of customer requirements,
            "green": count of GREEN (full match >= 0.85),
            "yellow": count of YELLOW (partial match >= 0.65),
            "red": count of RED (no match < 0.65),
            "pct_green": percentage of green matches,
            "pct_partial": percentage of yellow matches,
            "pct_red": percentage of red matches,
            "details": list of classified matches
        }
    """
    try:
        # Get best matches from database
        rows = list_best_matches(model_id, rfq_id, platform_id)

        # Classify each match
        classified = classify_coverage(FULL_MATCH_THRESHOLD, PARTIAL_MATCH_THRESHOLD, rows)

        # Count by color
        total = len(classified)
        green = sum(1 for r in classified if r["color"] == "GREEN")
        yellow = sum(1 for r in classified if r["color"] == "YELLOW")
        red = sum(1 for r in classified if r["color"] == "RED")

        # Calculate percentages (avoid division by zero)
        pct_green = round((green / total) * 100, 2) if total > 0 else 0.0
        pct_partial = round((yellow / total) * 100, 2) if total > 0 else 0.0
        pct_red = round((red / total) * 100, 2) if total > 0 else 0.0

        return {
            "total": total,
            "green": green,
            "yellow": yellow,
            "red": red,
            "pct_green": pct_green,
            "pct_partial": pct_partial,
            "pct_red": pct_red,
            "details": classified
        }

    except Exception as e:
        print(f"Error computing coverage summary: {e}")
        return {
            "total": 0,
            "green": 0,
            "yellow": 0,
            "red": 0,
            "pct_green": 0.0,
            "pct_partial": 0.0,
            "pct_red": 0.0,
            "details": [],
            "error": str(e)
        }


def get_coverage_color(similarity: float) -> str:
    """
    Get coverage color for a single similarity value.

    Args:
        similarity: Cosine similarity value (0.0 - 1.0)

    Returns:
        "GREEN" if >= 0.85, "YELLOW" if >= 0.65, "RED" otherwise
    """
    if similarity >= FULL_MATCH_THRESHOLD:
        return "GREEN"
    elif similarity >= PARTIAL_MATCH_THRESHOLD:
        return "YELLOW"
    else:
        return "RED"


def get_color_hex(color: str) -> str:
    """
    Get hex color code for coverage color.

    Args:
        color: "GREEN", "YELLOW", "RED", or "GRAY"

    Returns:
        Hex color code string
    """
    colors = {
        "GREEN": "#4CAF50",
        "YELLOW": "#FFC107",
        "RED": "#F44336",
        "GRAY": "#BDBDBD"
    }
    return colors.get(color.upper(), colors["GRAY"])
