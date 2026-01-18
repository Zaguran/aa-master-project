"""
Embedding Agent - Generate vector embeddings using Ollama
Version: 1.70
"""

import sys
import os
import hashlib
import requests
import time
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.db_bridge.database import (
    get_or_create_embedding_model,
    get_nodes_for_embedding,
    insert_embedding,
    update_agent_heartbeat
)


def normalize_text(text: str, max_chars: int = 4000) -> str:
    """
    Normalize text for embedding.

    - Replace \\r\\n with \\n
    - Strip line edges
    - Reduce multiple whitespace
    - Truncate to max_chars
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Strip lines and join
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Reduce whitespace
    text = re.sub(r'\s+', ' ', text)

    # Truncate if needed
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0]  # Break at word boundary

    return text.strip()


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def l2_normalize(vector: list) -> list:
    """L2 normalize vector for cosine similarity."""
    import math
    magnitude = math.sqrt(sum(x*x for x in vector))
    if magnitude == 0:
        return vector
    return [x / magnitude for x in vector]


def get_embedding_from_ollama(text: str, model: str, ollama_url: str) -> list:
    """
    Get embedding from Ollama API.

    Args:
        text: Text to embed
        model: Model name (e.g., 'nomic-embed-text')
        ollama_url: Ollama API URL

    Returns:
        Embedding vector (list of floats)
    """
    url = f"{ollama_url}/api/embeddings"

    payload = {
        "model": model,
        "prompt": text
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        embedding = data.get('embedding', [])

        # L2 normalize
        embedding = l2_normalize(embedding)

        return embedding

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None


def run_once(model: str = 'nomic-embed-text',
            vector_dims: int = 768,
            scope: str = None,
            batch_size: int = 50,
            max_chars: int = 4000,
            only_missing: bool = True,
            dry_run: bool = False) -> dict:
    """
    Run embedding generation once.

    Args:
        model: Ollama model name
        vector_dims: Vector dimensions
        scope: 'customer', 'platform', or None (all)
        batch_size: Number of nodes to process
        max_chars: Maximum characters per text
        only_missing: Skip nodes with existing embeddings
        dry_run: Don't actually insert, just print

    Returns:
        Dict with stats: embedded, skipped, errors
    """
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')

    # Get or create model
    model_id = get_or_create_embedding_model(model, vector_dims, 'ollama')
    if not model_id:
        return {"embedded": 0, "skipped": 0, "errors": 1, "message": "Failed to get model_id"}

    # Get nodes
    nodes = get_nodes_for_embedding(
        scope=scope,
        only_missing=only_missing,
        model_id=model_id,
        limit=batch_size
    )

    print(f"[Embedding Agent] Processing {len(nodes)} nodes (model={model}, scope={scope})")

    embedded = 0
    skipped = 0
    errors = 0

    for i, node in enumerate(nodes):
        try:
            # Normalize text
            content = node.get('content', '')
            normalized = normalize_text(content, max_chars)

            if not normalized:
                skipped += 1
                continue

            # Compute hash
            content_hash = compute_hash(normalized)

            if dry_run:
                print(f"[DRY RUN] Would embed: {node.get('node_id')} (hash={content_hash[:8]}...)")
                continue

            # Get embedding from Ollama
            embedding = get_embedding_from_ollama(normalized, model, ollama_url)

            if not embedding:
                errors += 1
                print(f"[ERROR] Failed to get embedding for {node.get('node_id')}")
                continue

            # Check dimensions
            if len(embedding) != vector_dims:
                errors += 1
                print(f"[ERROR] Wrong dimensions: expected {vector_dims}, got {len(embedding)}")
                continue

            # Insert to DB
            success = insert_embedding(
                node_uuid=str(node['node_uuid']),
                model_id=model_id,
                content_hash=content_hash,
                embedding_vector=embedding
            )

            if success:
                embedded += 1
                print(f"[{i+1}/{len(nodes)}] Embedded: {node.get('node_id')}")
            else:
                errors += 1

            # Small delay to avoid overwhelming Ollama
            time.sleep(0.1)

        except Exception as e:
            errors += 1
            print(f"[ERROR] Processing {node.get('node_id', 'unknown')}: {e}")

    # Update heartbeat
    update_agent_heartbeat('embedding_agent', queue_size=0, details={
        'model': model,
        'scope': scope,
        'embedded': embedded,
        'errors': errors
    })

    return {
        "embedded": embedded,
        "skipped": skipped,
        "errors": errors
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Embedding Agent')
    parser.add_argument('--model', default='nomic-embed-text', help='Ollama model name')
    parser.add_argument('--dims', type=int, default=768, help='Vector dimensions')
    parser.add_argument('--scope', choices=['customer', 'platform', 'all'], default='all')
    parser.add_argument('--batch', type=int, default=50, help='Batch size')
    parser.add_argument('--max-chars', type=int, default=4000, help='Max characters')
    parser.add_argument('--only-missing', action='store_true', default=True)
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--loop', action='store_true', help='Run in loop')
    parser.add_argument('--sleep', type=int, default=60, help='Sleep seconds between loops')

    args = parser.parse_args()

    scope = None if args.scope == 'all' else args.scope

    if args.loop:
        print(f"[Embedding Agent] Starting loop mode (sleep={args.sleep}s)")
        while True:
            result = run_once(
                model=args.model,
                vector_dims=args.dims,
                scope=scope,
                batch_size=args.batch,
                max_chars=args.max_chars,
                only_missing=args.only_missing,
                dry_run=args.dry_run
            )
            print(f"[Loop] Result: {result}")
            time.sleep(args.sleep)
    else:
        result = run_once(
            model=args.model,
            vector_dims=args.dims,
            scope=scope,
            batch_size=args.batch,
            max_chars=args.max_chars,
            only_missing=args.only_missing,
            dry_run=args.dry_run
        )
        print(f"Result: {result}")
