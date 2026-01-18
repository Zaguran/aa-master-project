"""
Embedding Web Component
Version: 1.70
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.embedding.embedding_agent import run_once as embedding_run_once


def generate_embeddings(scope: str = 'all',
                       model: str = 'nomic-embed-text',
                       batch_size: int = 50) -> dict:
    """
    Generate embeddings for requirements.

    Args:
        scope: 'customer', 'platform', or 'all'
        model: Ollama model name
        batch_size: Number of nodes to process

    Returns:
        Dict with embedded, skipped, errors counts
    """
    scope_param = None if scope == 'all' else scope

    return embedding_run_once(
        model=model,
        vector_dims=768,
        scope=scope_param,
        batch_size=batch_size,
        only_missing=True,
        dry_run=False
    )
