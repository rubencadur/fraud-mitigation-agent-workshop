"""Vector search over the fraud_patterns collection (Atlas $vectorSearch, with
a local cosine-similarity fallback). Index management lives in `indexes`."""
from .queries import search_frauds
