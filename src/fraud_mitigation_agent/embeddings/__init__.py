"""Embedding generation. `manual` is the required baseline path; the optional
Atlas Automated Embeddings path lives in `automated_atlas` (imported directly,
not re-exported here, since it needs a live Atlas connection to be useful)."""
from .manual import deterministic_embedding, text_for_transaction
