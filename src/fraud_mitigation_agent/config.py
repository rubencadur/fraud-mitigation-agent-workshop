"""Central runtime configuration, loaded from environment variables / Colab Secrets.

Keeping all tunables in one dataclass means notebooks never hard-code a
database name or index name directly — they read `Settings.from_env()` once
and pass it around, so the same notebook works locally, in Colab, or against
a different Atlas project just by changing env vars.
"""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str | None = None
    database_name: str = "fraud_mitigation_agent_workshop"
    source_tag: str = "fraud_mitigation_agent_colab_workshop"
    vector_index_name: str = "fraud_vector_index"
    auto_embedding_index_name: str = "fraud_auto_embedding_index"
    embedding_dimensions: int = 8
    # llm_provider is documentation-only today: notebooks that want a real LLM
    # instantiate OpenAICompatibleProvider directly with these values. There is
    # no factory here that switches on llm_provider.
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None

    @classmethod
    def from_env(cls, **overrides):
        # `overrides` lets tests/notebooks pin specific values (e.g. an
        # in-memory database name) without touching the process environment.
        values = {
            "mongodb_uri": os.getenv("MONGODB_URI"),
            "database_name": os.getenv("FRAUD_MITIGATION_AGENT_DATABASE", "fraud_mitigation_agent_workshop"),
            "source_tag": os.getenv("FRAUD_MITIGATION_AGENT_SOURCE_TAG", "fraud_mitigation_agent_colab_workshop"),
            "vector_index_name": os.getenv("FRAUD_MITIGATION_AGENT_VECTOR_INDEX", "fraud_vector_index"),
            "auto_embedding_index_name": os.getenv("FRAUD_MITIGATION_AGENT_AUTO_INDEX", "fraud_auto_embedding_index"),
            "embedding_dimensions": int(os.getenv("FRAUD_MITIGATION_AGENT_EMBEDDING_DIMENSIONS", "8")),
            "llm_provider": os.getenv("LLM_PROVIDER", "mock"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "llm_base_url": os.getenv("LLM_BASE_URL"),
            "llm_model": os.getenv("LLM_MODEL"),
        }
        values.update(overrides)
        return cls(**values)
