import hashlib
import re
import numpy as np


def _token_value(token: str, dimensions: int):
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    values = np.frombuffer(digest, dtype=np.uint8)[:dimensions].astype(float)
    return (values / 127.5) - 1.0


def deterministic_embedding(text: str, dimensions: int = 8):
    """Deterministic workshop embedding; not a production semantic model."""
    tokens = re.findall(r"[a-zA-Z0-9_áéíóúñ-]+", (text or "").lower())
    if not tokens:
        return [0.0] * dimensions
    vector = np.zeros(dimensions, dtype=float)
    for token in tokens:
        vector += _token_value(token, dimensions)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return [0.0] * dimensions
    return (vector / norm).round(6).tolist()


def text_for_transaction(transaction: dict, signals: list[str] | None = None):
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
