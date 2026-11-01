# Agentic Workplace Assistant

An AI-powered employee assistant demonstrating agentic workflows, RAG-based knowledge retrieval, structured tool integrations, deterministic routing, access controls and human-in-the-loop approval.

## 1. Project Overview

This project implements an AI assistant for common employee requests across three categories:

1. **Policy and process questions:** Answers questions using an internal knowledge base.
2. **Structured record queries:** Retrieves employee-specific information such as leave balances, reimbursement status and assigned assets.
3. **Action requests:** Creates IT tickets or routes sensitive requests for human approval.

The system combines a locally hosted LLM with deterministic Python workflows and validation to demonstrate how an enterprise AI assistant can operate safely and transparently.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| LLM | Qwen 2.5 3B through Ollama |
| Embeddings | all-MiniLM through Ollama |
| Vector similarity | NumPy cosine similarity |
| Knowledge retrieval | Custom RAG implementation |
| Schema validation | Pydantic |
| Mock integrations | JSON-based structured data |
| Automated testing | Pytest |
| Evaluation | Deterministic scenario-based evaluator |

The project uses a lightweight Python orchestrator instead of a multi-agent framework. Routing, authorization, validation and approval decisions are handled deterministically.

## 3. Architecture

The application follows this workflow:

1. Employee submits a request through the Streamlit interface.
2. The intake layer validates the request.
3. A deterministic router classifies the request as a policy question, record query or action request.
4. The orchestrator applies security and safety checks.
5. The relevant workflow is executed:
   - Policy questions use RAG.
   - Record queries call structured data tools.
   - Action requests create tickets or enter human review.
6. The response is validated against a structured Pydantic schema.
7. The UI displays the answer, citations, tool activity and approval status.

See [docs/architecture.md](docs/architecture.md) for the detailed architecture.

## 4. Retrieval-Augmented Generation (RAG)

The knowledge base contains nine internal policy and process documents.

### Retrieval pipeline

- Documents are loaded from Markdown files.
- Text is split into chunks of approximately 180 words, with 30-word overlap.
- Each chunk is converted into a 384-dimensional embedding using all-MiniLM.
- Embeddings are stored locally in a JSON vector store.
- NumPy cosine similarity ranks relevant chunks.
- Superseded documents are excluded before retrieval ranking by default.
- The top two results are used to construct the LLM context.
- Context is capped at 300 words.
- A retrieval confidence threshold of 0.30 is used for abstention.

The LLM is instructed to answer using the retrieved context and provide document citations. When the evidence is insufficient, the assistant abstains rather than inventing an answer.

### Versioning and conflicting sources

The knowledge base includes both a superseded 2024 leave policy and the current 2026 policy. The retrieval layer filters superseded documents before ranking.

A seeded conflict also exists between the expense policy and finance FAQ regarding the meal reimbursement limit (₹250 versus ₹300). The assistant explicitly surfaces this discrepancy rather than silently choosing one value.

### Retrieval evaluation

Ten manually labelled queries were evaluated.

| Metric | Result |
|---|---:|
| Hit Rate @ 2 | 100% |
| Recall @ 2 | 100% |
| Precision @ 2 | 70% |

The results indicate that all expected documents were retrieved, although some additional retrieved documents were not relevant.

## 5. Structured Tools and Access Control

The assistant integrates with mock structured employee data stored in JSON files.

Supported operations:

- Retrieve leave balances.
- Retrieve reimbursement status.
- Retrieve assigned assets.
- Create IT tickets.
- Submit sensitive requests for human approval.

### Security controls

- Employee identity is checked before accessing structured records.
- Employees cannot retrieve another employee's records.
- Unauthenticated requests are denied.
- Action requests validate required fields and priority values.
- Duplicate ticket creation is prevented using request IDs.
- Sensitive changes are routed for human approval.
- Tool failures return controlled fallback responses.

**Demo limitation:** The application uses a fixed demo employee identity (`EMP001`). A production implementation should derive identity from a trusted SSO/JWT session rather than a user-provided value.

## 6. Human-in-the-Loop Workflow

Sensitive actions, such as updating bank details, are not executed automatically.

Instead, the assistant:

1. Identifies that the request requires approval.
2. Creates a pending human-review record.
3. Returns a transparent pending-approval response.

This keeps high-impact employee operations under human oversight.

## 7. Evaluation Framework

The evaluation suite contains 24 scenarios covering expected behaviour, security, retrieval, tool integrations and failure handling.

The suite uses deterministic assertions rather than an LLM judge. Assertions check response status, required strings, citations, record values, access-denial behaviour and expected tool outcomes.

### Predefined acceptance thresholds

Acceptance criteria are defined in `evals/evaluation_thresholds.json` and enforced automatically by the evaluator.

| Criterion | Required threshold |
|---|---:|
| Overall scenario pass rate | At least 90% |
| Mandatory scenarios | 100% |
| Critical security scenarios | 100% |

Critical security scenarios include E06, E14, E16, E17 and E21.

The evaluator returns a non-zero exit code if any acceptance threshold fails.

### Final evaluation results

| Evaluation | Result |
|---|---:|
| Total scenarios | 24 |
| Passed | 24 |
| Failed | 0 |
| Overall pass rate | 100% |
| Mandatory scenarios | 6/6 (100%) |
| Critical security scenarios | 5/5 (100%) |
| Acceptance thresholds | All passed |

### Six mandatory situations

1. Superseded policy: returns the current policy and avoids citing the old version.
2. Unanswerable question: abstains.
3. Conflicting sources: surfaces the discrepancy.
4. Entitlement boundary: denies unauthorized access without exposing the record.
5. Tool failure: returns a controlled and truthful fallback.
6. Ambiguous request: asks for clarification.

Additional scenarios cover prompt injection, multiple intents, invalid inputs, duplicate actions, unauthenticated access and incomplete requests.

### Regression testing

A deliberate regression was introduced by disabling the superseded-document filter.

The evaluation suite detected the issue:

- Broken version filter: 23/24 passed (95.83%).
- Superseded-policy scenario E02 failed.
- After restoring the filter: 24/24 passed (100%).

This demonstrates that the evaluation suite detects a meaningful retrieval regression.

### Evaluation files

- `evals/evaluation_suite.json` – scenario definitions.
- `evals/evaluation_thresholds.json` – predefined acceptance criteria.
- `evals/raw_results.json` – latest raw evaluation output.
- `evals/final_results.json` – final evaluation results.
- `evals/baseline_results.json` – baseline results.
- `evals/regression_results.json` – deliberately broken version-filter results.
- `evals/retrieval_evaluation.json` – manually labelled retrieval queries.
- `evals/retrieval_results_k2.json` – retrieval metrics at k=2.
- `evals/retrieval_results_k3.json` – retrieval metrics at k=3.
- `evals/performance_results.json` – performance benchmark results.

No model-based judge is used; therefore, model-judge calibration and agreement calculations are not applicable.

## 8. Performance and Cost

Performance was measured locally using five runs per workflow.

| Workflow | Median latency | Worst latency |
|---|---:|---:|
| Policy question | 6,076.59 ms | 6,271.66 ms |
| Structured record query | 0.58 ms | 0.91 ms |
| Ticket creation | 9.28 ms | 14.63 ms |

Policy-question latency is dominated by local LLM inference.

### Cost

- External LLM API cost: ₹0.
- External embedding API cost: ₹0.
- Vector storage: local JSON file.
- Structured data: local JSON files.
- Application hosting: local Streamlit instance.

This does not mean the solution has zero total operating cost. Electricity, hardware, maintenance and production infrastructure would add costs.

The benchmark uses five sequential runs per workflow. It does not represent concurrent production capacity or a load test.

See [docs/performance_and_cost.md](docs/performance_and_cost.md) for further details.

## 9. Setup and Run

### Prerequisites

- Python 3.12 or later (the project was developed and tested with Python 3.15.2).
- Ollama installed and running.
- Git (optional, for version control).

### Step 1: Clone the repository

```powershell
git clone <repository-url>
cd raapid-agentic-assistant
```

### Step 2: Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Download the local models

```powershell
ollama pull qwen2.5:3b
ollama pull all-minilm
```

Ensure Ollama is running before starting the application.

### Step 5: Build the knowledge-base vector store

Whenever knowledge-base documents are added or updated, rebuild the vector store:

```powershell
.\.venv\Scripts\python.exe -m app.vector_store
```

### Step 6: Run the application

```powershell
streamlit run app/main.py
```

The application will open in your browser.

### Step 7: Run automated tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Step 8: Run the evaluation suite

```powershell
.\.venv\Scripts\python.exe -m app.evaluator
```

### Step 9: Run retrieval evaluation

```powershell
.\.venv\Scripts\python.exe -m app.evaluate_retrieval
```

### Step 10: Run performance benchmarks

```powershell
.\.venv\Scripts\python.exe -m app.benchmark
```

## 10. Known Limitations and Future Improvements

The current implementation is a functional prototype using mock employee data and a local LLM.

Potential improvements for production readiness include:

- Integrating enterprise identity management and SSO.
- Replacing JSON mock data with secure enterprise APIs and databases.
- Adding role-based and attribute-based access control.
- Improving retrieval precision through better chunking, metadata filtering and reranking.
- Expanding conflict detection beyond the seeded expense-policy example.
- Adding automated vector-store refresh and document lifecycle management.
- Measuring latency under concurrent workloads.
- Adding monitoring, audit logs and production-grade observability.
- Implementing an approval interface for human reviewers.

## 11. Project Documentation

Additional documentation is available in the `docs/` directory:

- `architecture.md` – system architecture and technical design.
- `failure_log.md` – implementation failures, root causes and fixes.
- `tooling_disclosure.md` – development tools, AI assistance and design decisions.
- `performance_and_cost.md` – benchmark methodology, results and cost analysis.

## 12. Disclaimer

This is a demonstration prototype built for an AI product assignment. Employee records and policies are mock data created for evaluation. It is not connected to any real HR, finance or IT system.
