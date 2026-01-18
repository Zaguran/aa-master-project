"""
Matching Web Component
Version: 1.70
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.matching.matching_agent import run_once as matching_run_once
from agents.db_bridge.database import get_match_statistics


def run_matching(model: str = 'nomic-embed-text',
                top_k: int = 5,
                full_threshold: float = 0.85,
                partial_threshold: float = 0.65) -> dict:
    """
    Run matching engine.

    Args:
        model: Model name
        top_k: Top K matches per customer req
        full_threshold: GREEN threshold
        partial_threshold: YELLOW threshold

    Returns:
        Dict with matched, errors counts
    """
    return matching_run_once(
        model=model,
        vector_dims=768,
        top_k=top_k,
        full_threshold=full_threshold,
        partial_threshold=partial_threshold,
        clear_existing=True,
        dry_run=False
    )


def get_coverage_summary(model_id: int = 1) -> dict:
    """
    Get coverage summary from matches.

    Args:
        model_id: Embedding model ID

    Returns:
        Dict with GREEN, YELLOW, RED counts and percentages
    """
    return get_match_statistics(model_id)
