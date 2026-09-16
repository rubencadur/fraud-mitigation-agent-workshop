# Fraud Mitigation Agent Workshop — Project Specification for AI Continuity

## 1. Purpose of this document

This document is the authoritative continuity brief for the `fraud-mitigation-agent-workshop` repository. It is written for a future developer, architect, or LLM that must understand the project, execute it, review it, extend it, or repair it without relying on undocumented conversation history.

The repository is an educational, synthetic-data implementation of a Fraud Mitigation Agent: a hybrid fraud-detection flow built with Python, MongoDB Atlas Vector Search, optional Automated Embeddings, deterministic scoring, auditable evidence, and an optional LLM layer.

This is a workshop reference implementation, not a production fraud platform. It intentionally favors transparency, small modules, reproducibility, and Google Colab compatibility over throughput, security hardening, and production deployment completeness.

## 2. Project identity

* **Project:** Fraud Mitigation Agent Workshop
* **Repository directory:** `fraud-mitigation-agent-workshop`
* **Primary language:** Python 3.10+
* **Primary runtime:** Google Colab or a local Python environment
* **Primary datastore:** MongoDB Atlas; an in-memory fallback exists for offline demonstrations
* **LLM requirement:** none for the core path; `MockLLMProvider` is the default
* **Data policy:** synthetic data only
* **Core objective:** teach the progression from a basic agent to an auditable hybrid fraud-decision engine
* **Primary user:** a workshop participant, solutions architect, developer, or AI agent continuing the implementation

## 3. Business and technical context

Fraud Mitigation Agent addresses a common fraud-detection problem: evaluating a transaction in isolation is insufficient. A useful decision requires customer context, historical fraud similarity, behavioral deviations, configurable rules, and an explanation that can be audited later.

The conceptual design came from an executive and technical fraud-detection report supplied with the project. The report describes a production-oriented flow with:

* customer context such as known devices, IPs, locations, velocity counters, and average amounts;
* historical fraud patterns represented as vectors;
* rules and weights stored as configuration rather than hard-coded prompts;
* a hybrid score combining vector similarity, behavioral signals, and rules;
* final outcomes and evidence for feedback and audit;
* a future feedback loop using confirmed fraud, customer claims, investigations, and step-up outcomes.

The report contains production sizing, latency, and infrastructure claims. Those values are design hypotheses only. They must be validated with representative data and load tests before being used for a real system.

## 4. Scope and non-goals

### In scope

* A complete incremental workshop path from agent basics to decisioning.
* Reusable Python modules under `src/fraud_mitigation_agent/`.
* MongoDB collections and access patterns for the workshop.
* Manual embeddings and manual Vector Search.
* Optional Atlas Automated Embeddings path with fallback.
* Deterministic behavior analysis, rules, score calculation, decisions, and audit evidence.
* An offline mock LLM path with no external API key.
* Synthetic fixtures for normal, step-up, and risky scenarios.
* Basic evaluation of precision, recall, and confusion-matrix counts.
* Notebooks suitable for Google Colab.

### Explicitly out of scope

* Production-grade fraud ML training.
* Real customer data, real Bancolombia data, or real credentials.
* Guaranteed sub-500 ms latency.
* Regulatory certification or model-risk approval.
* Authentication, authorization, secrets management, or payment execution.
* A production event bus, retry system, distributed idempotency store, or deployment manifests.
* A claim that Atlas Free is suitable for production workloads.
* Treating an LLM response as the source of truth for a risk decision.

## 5. Design principles

1. **Deterministic decision core.** The final score and decision must be reproducible from stored inputs and configuration.
2. **LLM is optional.** The system must work without an external model, network access, or API key.
3. **Tools before prose.** Context and evidence are retrieved through explicit tools; prompts do not fabricate facts.
4. **Evidence is first-class.** Every decision should be explainable through signals, rules, similarity results, configuration versions, and a trace.
5. **Configuration over redeployment.** Weights and thresholds are stored in `risk_rules_config` so the workshop can demonstrate dynamic policy changes.
6. **Manual Vector Search first.** Precomputed embeddings and a normal vector index are the mandatory learning path.
7. **Advanced capabilities must degrade gracefully.** Automated Embeddings is optional and must not block the workshop.
8. **Synthetic by default.** Fixtures are intentionally artificial and must remain so.
9. **Small composable modules.** Each tool should have one responsibility and return a predictable `ToolResult`.
10. **Do not confuse a workshop with production.** Any production claim requires separate testing, security review, and operational design.

## 6. Repository map

```text
fraud-mitigation-agent-workshop/
├── README.md
├── PROJECT_SPECIFICATION.md
├── requirements.txt
├── pyproject.toml
├── run_tests.py
├── .gitignore
├── docs/
│   ├── contracts.md
│   ├── setup_atlas_colab.md
│   ├── vector_search_paths.md
│   └── workshop_agenda.md
├── notebooks/
│   ├── core/
│   │   ├── 00_setup_workshop.ipynb
│   │   ├── 01_prompt_agent.ipynb
│   │   ├── 02_transaction_tool.ipynb
│   │   ├── 03_context_tools.ipynb
│   │   ├── 04_rule_tools.ipynb
│   │   ├── 05_behavior_analysis.ipynb
│   │   ├── 06_vector_search_manual.ipynb
│   │   ├── 07_dynamic_scoring.ipynb
│   │   └── 08_decision_engine.ipynb
│   └── advanced/
│       ├── 06_automated_embeddings_atlas.ipynb
│       ├── 09_realtime_fraud_engine.ipynb
│       └── 10_evaluation_precision_recall.ipynb
├── src/fraud_mitigation_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── audit.py
│   ├── config.py
│   ├── db.py
│   ├── engine.py
│   ├── evaluation.py
│   ├── local.py
│   ├── models.py
│   ├── scoring.py
│   ├── synthetic.py
│   ├── embeddings/
│   │   ├── manual.py
│   │   └── automated_atlas.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── mock_provider.py
│   │   └── openai_compatible.py
│   ├── tools/
│   │   ├── _common.py
│   │   ├── behavior.py
│   │   ├── customer_context.py
│   │   ├── decisions.py
│   │   ├── rules.py
│   │   ├── similarity.py
│   │   └── transactions.py
│   └── vector_search/
│       ├── indexes.py
│       └── queries.py
└── tests/
    ├── test_embeddings.py
    ├── test_scoring.py
    └── test_workflow.py
```

## 7. Execution model

The reference flow is:

```text
transaction_id
    │
    ▼
get_transaction
    │
    ▼
get_customer_state
    │
    ├── evaluate_rules
    ├── analyze_behavior
    └── find_similar_fraud
             │
             ▼
       score_components
             │
             ▼
       decision_from_score
             │
             ▼
       make_evidence / persist_evidence
             │
             ▼
       final_outcome + risk_evidence
```

The `FraudAgent` orchestrates the flow. The agent does not independently invent a risk score. It executes explicit tools, passes their structured results into the deterministic scoring layer, and optionally uses an LLM only to explain the resulting evidence.

`RealtimeFraudEngine` is a synchronous reference wrapper around the same flow. It is not a production realtime service.

## 8. Data model and collections

The MongoDB database name defaults to `fraud_mitigation_agent_workshop` and can be changed with `FRAUD_MITIGATION_AGENT_DATABASE`.

### 8.1 `transactions`

One document per synthetic transaction.

Important fields:

```json
{
  "tx_id": "tx-risky-001",
  "customer_id": "customer-risky",
  "amount": 5000000,
  "currency": "COP",
  "timestamp": "2025-01-15T03:00:00Z",
  "channel": "mobile",
  "ip": "203.0.113.30",
  "device_id": "device-new-003",
  "geo_km_from_usual": 9000,
  "ground_truth_fraud": true,
  "fraud_signature_text": "new device new ip impossible travel odd hour high amount",
  "embedding": [-0.489045, -0.30894, 0.394391, -0.035495, -0.30894, 0.126205, -0.063103, 0.627082],
  "source_tag": "fraud_mitigation_agent_synthetic"
}
```

`ground_truth_fraud` is a fixture label for evaluation only. It must not be used as a decision input.

### 8.2 `customer_state`

Current synthetic customer baseline used by context and behavior tools.

```json
{
  "customer_id": "customer-risky",
  "usual_ips": ["198.51.100.30"],
  "usual_devices": ["device-risky-001"],
  "usual_countries": ["MX"],
  "avg_amount": 2500,
  "p95_amount": 12000,
  "transactions_24h": 2,
  "transactions_10m": 1,
  "source_tag": "fraud_mitigation_agent_synthetic"
}
```

A future production model may replace the simple arrays with richer embedded objects such as first-seen timestamps, counts, geolocation, device type, confidence, and recency.

### 8.3 `fraud_patterns`

Historical synthetic fraud signatures for similarity search.

Required fields:

* `tx_id`
* `fraud_confirmed`
* `fraud_type`
* `fraud_signature_text`
* `embedding`
* `source_tag`

The current manual embedding dimension is 8 to keep the workshop lightweight. Do not describe it as a production semantic embedding.

### 8.4 `risk_rules_config`

Versioned policy configuration.

Example:

```json
{
  "config_id": "risk_rules_config",
  "version": "demo-v1",
  "enabled": true,
  "thresholds": {
    "high_amount": 1000000,
    "amount_multiplier": 5,
    "impossible_travel_km": 500,
    "velocity_10m": 5
  },
  "weights": {
    "vector": 0.4,
    "signals": 0.35,
    "rules": 0.25
  },
  "decision_thresholds": {
    "approve_max": 39,
    "step_up_max": 69
  },
  "source_tag": "fraud_mitigation_agent_synthetic"
}
```

The current implementation reads the weights from configuration. The decision helper currently uses its default `DecisionPolicy` thresholds; future work should make the configured thresholds flow fully into `decision_from_score`.

### 8.5 `final_outcome`

Latest decision per transaction. This is a learning and operational summary collection.

Expected fields include:

* `transaction_id`
* `decision`
* `risk_score`
* `reason_codes`
* `evidence_id`
* `source_tag`

### 8.6 `risk_evidence`

Immutable-style audit records for each decision attempt.

Expected fields include:

* `evidence_id`
* `transaction_id`
* `created_at`
* `decision`
* `risk_score`
* `components`
* `weights`
* `signals`
* `triggered_rules`
* `similarity`
* `trace`
* `config_version`
* `policy_version`

A production system should define retention, immutability, access control, PII treatment, and correlation IDs separately.

## 9. Scoring contract

The conceptual formula is:

```text
risk_score = Vector × 0.40 + Signals × 0.35 + Rules × 0.25
```

All three components are normalized to `[0, 100]` before weighting.

### Vector component

The current implementation converts cosine similarity from `[-1, 1]` to `[0, 100]` using:

```text
vector_risk = (similarity + 1) × 50
```

This is a teaching transformation, not a calibrated probability.

### Signals component

Behavior signals have explicit numeric scores. Current examples include:

* amount deviation: 35;
* IP deviation: 20;
* device deviation: 25;
* geo deviation: 25.

The sum is bounded to `[0, 100]`.

### Rules component

Rules map severity to points:

* low: 15;
* medium: 30;
* high: 50;
* critical: 70.

The sum is bounded to `[0, 100]`.

### Decision contract

The repository uses risk semantics:

* `risk_score <= 39`: `APPROVE`;
* `40 <= risk_score <= 69`: `STEP-UP`;
* `risk_score > 69`: `DENY`.

This is intentionally explicit because the source report contains an inconsistent verbal mapping in one section. A high risk score must result in a stricter decision. Any future change must update the tests, docs, notebooks, and policy configuration together.

## 10. Tool contracts

Every tool should return a `ToolResult` with:

```json
{
  "tool_name": "tool_name",
  "status": "success|error",
  "data": {},
  "evidence": [],
  "latency_ms": 0.0,
  "error": null
}
```

Current tools:

| Tool | Responsibility |
|---|---|
| `get_transaction` | Fetch one transaction by `tx_id`. |
| `get_customer_state` | Fetch one customer baseline by `customer_id`. |
| `get_rules_config` | Fetch the current risk policy document. |
| `evaluate_rules` | Apply configurable rules to transaction plus customer state. |
| `analyze_behavior` | Compare transaction features with the customer baseline. |
| `find_similar_fraud` | Run Atlas Vector Search or local cosine fallback. |
| `score_and_decide` | Combine components, produce a decision, and build evidence. |
| `persist_decision` | Persist evidence and the latest final outcome. |

When adding a tool:

1. Keep the tool single-purpose.
2. Return structured data, not prose.
3. Include useful evidence fields.
4. Handle expected lookup failures explicitly.
5. Add an offline test using `InMemoryDB`.
6. Do not let an LLM directly bypass the deterministic contract.

## 11. Vector Search paths

### 11.1 Mandatory manual path

The manual path is implemented in:

* `src/fraud_mitigation_agent/embeddings/manual.py`
* `src/fraud_mitigation_agent/vector_search/indexes.py`
* `src/fraud_mitigation_agent/vector_search/queries.py`
* `notebooks/core/06_vector_search_manual.ipynb`

It stores an embedding array in `fraud_patterns.embedding`, creates a vector index definition, and uses `$vectorSearch` when Atlas is available. If aggregation is unavailable, the workshop falls back to local cosine similarity so that the learning path remains runnable.

### 11.2 Optional Automated Embeddings path

The optional path is implemented in:

* `src/fraud_mitigation_agent/embeddings/automated_atlas.py`
* `notebooks/advanced/06_automated_embeddings_atlas.ipynb`

It demonstrates an `autoEmbed` index definition and text-based vector search. Availability can depend on Atlas feature support, region, cluster configuration, API version, and preview status. It must never replace the manual path as the baseline.

## 12. LLM architecture

### Default provider

`MockLLMProvider` is deterministic, local, and requires no API key. It is the only provider required to complete the workshop.

### Optional provider

`OpenAICompatibleProvider` can call an OpenAI-compatible chat endpoint when configured with:

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...
```

No key or endpoint should be committed to GitHub. The optional provider is for explanation and experimentation; it is not trusted with the final risk decision.

### Future provider work

A future provider abstraction may add structured tool calling. If implemented, preserve these invariants:

* tool arguments must be validated;
* tools must be allow-listed;
* tool results must be recorded in the trace;
* the model cannot modify score weights directly;
* the final decision must still be generated by deterministic code;
* prompt injection from transaction fields must be treated as untrusted input.

## 13. Notebook progression

### Core route

| Notebook | Learning objective |
|---|---|
| `00_setup_workshop` | Install dependencies, configure Colab/Atlas, seed synthetic data. |
| `01_prompt_agent` | Introduce the agent and offline provider. |
| `02_transaction_tool` | Retrieve one transaction through a tool. |
| `03_context_tools` | Add customer state and historical context. |
| `04_rule_tools` | Apply versioned rules. |
| `05_behavior_analysis` | Detect deviations from a customer baseline. |
| `06_vector_search_manual` | Add manual embeddings and similarity search. |
| `07_dynamic_scoring` | Combine vector, signal, and rule components. |
| `08_decision_engine` | Produce decision, reason codes, trace, and audit evidence. |

### Advanced route

| Notebook | Learning objective |
|---|---|
| `06_automated_embeddings_atlas` | Explore optional Atlas Automated Embeddings with fallback. |
| `09_realtime_fraud_engine` | Wrap the flow in a realtime reference engine. |
| `10_evaluation_precision_recall` | Evaluate synthetic outcomes with precision and recall. |

## 14. Environment and execution

### Local installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m pytest -q
```

### Atlas configuration

```bash
export MONGODB_URI='mongodb+srv://<user>:<password>@<cluster>/?retryWrites=true&w=majority'
export FRAUD_MITIGATION_AGENT_DATABASE='fraud_mitigation_agent_workshop'
```

Never print `MONGODB_URI`. In Google Colab, use Colab Secrets.

### Offline execution

No Atlas connection is required for the basic workflow. Use:

```python
from fraud_mitigation_agent.local import InMemoryDB
from fraud_mitigation_agent.synthetic import seed_demo_data
from fraud_mitigation_agent.agent import FraudAgent

db = InMemoryDB()
seed_demo_data(db, reset=True)
result = FraudAgent(db).analyze('tx-risky-001', persist=True)
```

## 15. Synthetic scenarios

The fixtures currently include:

* `tx-normal-001`: familiar IP, familiar device, ordinary amount, low-risk baseline.
* `tx-stepup-001`: elevated amount and somewhat unusual time/behavior, intended as an intermediate scenario.
* `tx-risky-001`: very high amount, new IP, new device, odd hour, and extreme geographic deviation; intended to produce `DENY`.

The fixture data is illustrative. Do not infer model quality from three examples.

## 16. Testing requirements

Any meaningful code change should preserve:

* deterministic embedding behavior;
* score bounds `[0, 100]`;
* decision boundary behavior;
* offline workflow execution;
* evidence persistence;
* valid notebook JSON;
* no requirement for an external LLM.

Current tests:

* `tests/test_embeddings.py`
* `tests/test_scoring.py`
* `tests/test_workflow.py`

Recommended future tests:

* missing transaction and missing customer behavior;
* malformed rule configuration;
* empty Vector Search result;
* Atlas aggregation failure and fallback;
* custom decision thresholds from configuration;
* duplicate persistence and idempotency;
* evaluation edge cases with no positive labels;
* prompt-injection-like values in transaction fields;
* latency instrumentation and timeout behavior.

## 17. Known limitations and technical debt

1. The in-memory database implements only the subset required by the workshop.
2. Local similarity is not equivalent to Atlas Vector Search.
3. Manual embeddings are deterministic hash-based vectors, not a semantic production model.
4. The optional Automated Embeddings API may vary by Atlas availability and version.
5. `risk_rules_config.decision_thresholds` is stored but the current decision helper does not yet consume it dynamically.
6. `persist_decision` uses a replacement/upsert for `final_outcome`, but evidence records are append-only inserts and need a production idempotency strategy.
7. There is no authentication or authorization layer.
8. There are no production deployment files, service-level timeouts, retries, queues, or tracing exporters.
9. The mock LLM does not implement real tool-calling semantics.
10. Evaluation is fixture-based and statistically meaningless for production claims.
11. The current code is synchronous.
12. The repository does not contain the original confidential report; the report is design context, not runtime input.

## 18. Recommended next increments

Prioritize work in this order:

### Increment 1 — Policy correctness

* Pass `decision_thresholds` from `risk_rules_config` into `decision_from_score`.
* Add tests proving that configuration changes alter only policy boundaries, not raw component calculations.
* Add an explicit `policy_version` to every outcome.

### Increment 2 — Contract hardening

* Introduce typed input/output models with validation.
* Validate transaction identifiers and numeric ranges.
* Make tool errors machine-readable with stable error codes.

### Increment 3 — Idempotency and audit quality

* Add a request or event ID.
* Make evidence writes idempotent for retries.
* Separate decision attempt, final outcome, and later confirmed outcome.
* Add immutable event timestamps and correlation IDs.

### Increment 4 — Retrieval quality

* Replace manual embeddings with a documented embedding model in a controlled experiment.
* Compare local fallback against Atlas Vector Search on a larger synthetic corpus.
* Add relevance metrics for top-k retrieval.

### Increment 5 — Evaluation

* Generate a larger synthetic population with controlled fraud prevalence.
* Add threshold sweeps and precision-recall curves.
* Measure false-positive cost, false-negative cost, and step-up rate.
* Add calibration analysis; similarity is not probability.

### Increment 6 — Production architecture study

* Add an API boundary and schema versioning.
* Add timeout budgets and circuit breakers.
* Add structured logs and distributed traces.
* Evaluate dedicated Atlas Search Nodes and workload isolation.
* Define PII minimization, encryption, retention, access control, and incident response.

## 19. Safety and security rules for future contributors

* Never commit `MONGODB_URI`, `LLM_API_KEY`, passwords, certificates, or exported customer records.
* Never replace synthetic fixtures with real customer data in a public repository.
* Never claim that the workshop is production-ready because the demo returns a plausible decision.
* Never let a natural-language model override a deterministic policy without an explicit, tested design change.
* Never expose full transaction or customer documents in logs by default.
* Treat all external text fields as untrusted content.
* Keep Atlas Free usage limited to workshop data and delete temporary network access after the exercise.

## 20. Continuation protocol for another LLM

A future LLM should follow this sequence before modifying the project:

1. Read this file completely.
2. Read `README.md`, `docs/contracts.md`, and the relevant notebook.
3. Inspect the target source module and its tests.
4. Run the offline workflow before changing behavior.
5. State whether the requested change is core, advanced, documentation-only, or production architecture.
6. Preserve the deterministic decision boundary unless the request explicitly changes policy.
7. Add or update tests before declaring completion.
8. Validate imports, Python compilation, notebook JSON, and offline execution.
9. Update this specification when architecture, contracts, limitations, or execution steps change.
10. Never invent Atlas capabilities or production performance numbers; label assumptions and verify them separately.

## 21. Suggested handoff prompt

The following prompt can be given to another LLM together with the repository:

```text
You are continuing the Fraud Mitigation Agent Workshop repository.

First read PROJECT_SPECIFICATION.md, README.md, docs/contracts.md, and the relevant source/tests. This is an educational synthetic-data project for hybrid fraud detection using MongoDB Atlas, optional Vector Search/Automated Embeddings, deterministic scoring, auditable evidence, and an optional LLM layer.

Important invariants:
- The core path must work without an external LLM.
- MockLLMProvider is the default offline provider.
- The final decision is deterministic and evidence-backed.
- The manual Vector Search path is mandatory.
- Automated Embeddings is optional and must have a fallback.
- Never use real customer data or commit credentials.
- A high risk score must not produce APPROVE.

Before editing:
1. Reproduce the offline workflow with InMemoryDB and synthetic fixtures.
2. Identify affected contracts and tests.
3. Make the smallest coherent change.
4. Add tests and update docs/specification when behavior changes.
5. Validate compilation, tests, notebook JSON, and offline execution.

Requested task:
<describe the new task here>
```

## 22. Definition of done

A change is complete when:

* the implementation is in the correct module;
* the public contract is documented;
* the offline workflow still runs;
* tests cover the changed behavior;
* notebook examples remain executable or are explicitly marked as requiring Atlas;
* no credentials or real data were added;
* limitations and assumptions are stated;
* this file is updated when the project context changes.
