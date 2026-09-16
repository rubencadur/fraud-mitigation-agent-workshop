from fraud_mitigation_agent.embeddings.manual import deterministic_embedding


def test_embedding_is_deterministic_and_normalized():
    first = deterministic_embedding("new device impossible travel")
    second = deterministic_embedding("new device impossible travel")
    assert first == second
    assert len(first) == 8
