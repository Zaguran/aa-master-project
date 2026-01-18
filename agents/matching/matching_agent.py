"""
Matching Agent - Match customer and platform requirements using embeddings
Version: 1.70
"""

import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.db_bridge.database import (
    get_or_create_embedding_model,
    get_embeddings_by_scope,
    insert_match,
    clear_matches,
    update_agent_heartbeat
)


def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1, vec2: Embedding vectors (already L2 normalized)

    Returns:
        Similarity score (0-1)
    """
    if len(vec1) != len(vec2):
        return 0.0

    # Since vectors are L2 normalized, cosine = dot product
    return sum(a * b for a, b in zip(vec1, vec2))


def classify_match(similarity: float, full_threshold: float = 0.85, partial_threshold: float = 0.65) -> str:
    """
    Classify match based on similarity score.

    Args:
        similarity: Cosine similarity score
        full_threshold: Threshold for GREEN (full match)
        partial_threshold: Threshold for YELLOW (partial match)

    Returns:
        'GREEN', 'YELLOW', or 'RED'
    """
    if similarity >= full_threshold:
        return 'GREEN'
    elif similarity >= partial_threshold:
        return 'YELLOW'
    else:
        return 'RED'


def parse_embedding_vector(embedding_str: str) -> list:
    """
    Parse pgvector string to list of floats.

    Args:
        embedding_str: String like '[0.1,0.2,0.3]'

    Returns:
        List of floats
    """
    if isinstance(embedding_str, list):
        return embedding_str

    # Remove brackets and split
    embedding_str = str(embedding_str).strip('[]')
    return [float(x) for x in embedding_str.split(',')]


def run_once(model: str = 'nomic-embed-text',
            vector_dims: int = 768,
            top_k: int = 5,
            full_threshold: float = 0.85,
            partial_threshold: float = 0.65,
            clear_existing: bool = True,
            dry_run: bool = False) -> dict:
    """
    Run matching once.

    Args:
        model: Model name
        vector_dims: Vector dimensions
        top_k: Number of top matches to store per customer req
        full_threshold: GREEN threshold
        partial_threshold: YELLOW threshold
        clear_existing: Clear existing matches before running
        dry_run: Don't actually insert

    Returns:
        Dict with stats
    """
    # Get model ID
    model_id = get_or_create_embedding_model(model, vector_dims, 'ollama')
    if not model_id:
        return {"matched": 0, "errors": 1, "message": "Failed to get model_id"}

    # Clear existing matches if requested
    if clear_existing and not dry_run:
        clear_matches(model_id)
        print(f"[Matching Agent] Cleared existing matches for model_id={model_id}")

    # Get embeddings
    print(f"[Matching Agent] Loading embeddings...")
    customer_embeddings = get_embeddings_by_scope(model_id, 'customer')
    platform_embeddings = get_embeddings_by_scope(model_id, 'platform')

    print(f"[Matching Agent] Customer: {len(customer_embeddings)}, Platform: {len(platform_embeddings)}")

    if not customer_embeddings or not platform_embeddings:
        return {"matched": 0, "errors": 0, "message": "No embeddings found"}

    matched = 0
    errors = 0

    for i, customer in enumerate(customer_embeddings):
        try:
            customer_vec = parse_embedding_vector(customer['embedding'])
            customer_uuid = customer['node_uuid']
            customer_id = customer['node_id']

            # Compute similarities to all platform reqs
            similarities = []

            for platform in platform_embeddings:
                platform_vec = parse_embedding_vector(platform['embedding'])
                platform_uuid = platform['node_uuid']

                similarity = cosine_similarity(customer_vec, platform_vec)

                similarities.append({
                    'platform_uuid': platform_uuid,
                    'platform_id': platform['node_id'],
                    'similarity': similarity
                })

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)

            # Take top K
            top_matches = similarities[:top_k]

            if dry_run:
                print(f"[DRY RUN] {customer_id} -> {len(top_matches)} matches")
                for rank, match in enumerate(top_matches, 1):
                    classification = classify_match(match['similarity'], full_threshold, partial_threshold)
                    print(f"  [{rank}] {match['platform_id']}: {match['similarity']:.3f} ({classification})")
                continue

            # Insert matches
            for rank, match in enumerate(top_matches, 1):
                classification = classify_match(match['similarity'], full_threshold, partial_threshold)

                success = insert_match(
                    model_id=model_id,
                    customer_uuid=customer_uuid,
                    platform_uuid=match['platform_uuid'],
                    similarity=match['similarity'],
                    rank=rank,
                    classification=classification
                )

                if success:
                    matched += 1
                else:
                    errors += 1

            print(f"[{i+1}/{len(customer_embeddings)}] Matched {customer_id} to {len(top_matches)} platforms")

        except Exception as e:
            errors += 1
            print(f"[ERROR] Matching {customer.get('node_id', 'unknown')}: {e}")

    # Update heartbeat
    update_agent_heartbeat('matching_agent', queue_size=0, details={
        'model': model,
        'matched': matched,
        'errors': errors
    })

    return {
        "matched": matched,
        "errors": errors
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Matching Agent')
    parser.add_argument('--model', default='nomic-embed-text', help='Model name')
    parser.add_argument('--dims', type=int, default=768, help='Vector dimensions')
    parser.add_argument('--topk', type=int, default=5, help='Top K matches')
    parser.add_argument('--full-th', type=float, default=0.85, help='Full match threshold')
    parser.add_argument('--partial-th', type=float, default=0.65, help='Partial match threshold')
    parser.add_argument('--no-clear', action='store_true', help='Do not clear existing matches')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--loop', action='store_true', help='Run in loop')
    parser.add_argument('--sleep', type=int, default=300, help='Sleep seconds')

    args = parser.parse_args()

    if args.loop:
        print(f"[Matching Agent] Starting loop mode (sleep={args.sleep}s)")
        while True:
            result = run_once(
                model=args.model,
                vector_dims=args.dims,
                top_k=args.topk,
                full_threshold=args.full_th,
                partial_threshold=args.partial_th,
                clear_existing=not args.no_clear,
                dry_run=args.dry_run
            )
            print(f"[Loop] Result: {result}")
            time.sleep(args.sleep)
    else:
        result = run_once(
            model=args.model,
            vector_dims=args.dims,
            top_k=args.topk,
            full_threshold=args.full_th,
            partial_threshold=args.partial_th,
            clear_existing=not args.no_clear,
            dry_run=args.dry_run
        )
        print(f"Result: {result}")
