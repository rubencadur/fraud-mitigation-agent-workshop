"""Manual (non-Atlas) embedding generation: the mandatory baseline vector path.

No embedding model, API key or network call is required — vectors are
derived purely by hashing tokens, which keeps the whole vector-search
workshop path free and fully offline. See embeddings/automated_atlas.py for
the optional path that instead calls a real embedding model via Atlas.
"""
import hashlib
import re
import numpy as np


def _token_value(token: str, dimensions: int):
    # SHA-256 gives a stable, uniformly-distributed byte sequence per token;
    # scaling bytes [0, 255] to roughly [-1, 1] turns it into a small vector
    # that's summed across tokens below. Same token always maps to the same
    # vector, which is what makes the whole embedding deterministic.
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    values = np.frombuffer(digest, dtype=np.uint8)[:dimensions].astype(float)
    return (values / 127.5) - 1.0


def deterministic_embedding(text: str, dimensions: int = 8):
    """Deterministic workshop embedding; not a production semantic model.

    It has no real semantic understanding (no training, no model) — it only
    guarantees that similar/overlapping token sets end up as nearby vectors,
    which is enough to demonstrate vector search end-to-end in the workshop.
    """
    tokens = re.findall(r"[a-zA-Z0-9_áéíóúñ-]+", (text or "").lower())
    if not tokens:
        return [0.0] * dimensions
    vector = np.zeros(dimensions, dtype=float)
    for token in tokens:
        vector += _token_value(token, dimensions)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return [0.0] * dimensions
    # L2-normalize so vector magnitude never leaks token count into the
    # cosine similarity comparison — only direction (token overlap) matters.
    return (vector / norm).round(6).tolist()


def text_for_transaction(transaction: dict, signals: list[str] | None = None):
    """Turn a transaction's raw fields into short text to embed, when no
    fraud_signature_text was precomputed (see tools/similarity.py)."""
    signals = signals or []
    parts = [
        f"channel {transaction.get('channel', 'unknown')}",
        f"amount {transaction.get('amount', 0)} {transaction.get('currency', 'COP')}",
        f"ip {transaction.get('ip', 'unknown')}",
        f"device {transaction.get('device_id', 'unknown')}",
        f"geo_distance {transaction.get('geo_km_from_usual', 0)} km",
    ]
    parts.extend(signals)
    return " ".join(parts)
