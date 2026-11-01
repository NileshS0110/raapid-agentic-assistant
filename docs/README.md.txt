
# Employee AI Assistant

A locally runnable employee-facing AI assistant prototype built for the RAAPID Agentic AI assignment.

The assistant handles policy questions, structured employee-record queries and employee action requests through deterministic routing, retrieval-augmented generation (RAG), Python tools and human-in-the-loop controls.

## Key capabilities

- **Policy and process questions:** RAG over nine internal policy and process documents, with source citations.
- **Structured record queries:** Retrieves employee leave balances, reimbursement claims and assigned assets from mock JSON data.
- **Action requests:** Creates IT support tickets with input validation and duplicate prevention.
- **Human-in-the-loop:** Escalates sensitive requests for human review rather than executing them automatically.
- **Security controls:** Employee access checks, prompt-injection phrase detection and deterministic routing.
- **Failure handling:** Abstains on unsupported questions and returns graceful fallbacks when tools fail.
- **Evaluation:** 24 deterministic scenarios, including all six mandatory assignment scenarios.
- **Regression testing:** Demonstrates detection of a deliberately introduced superseded-policy retrieval bug.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend and orchestration | Python |
| LLM | Qwen2.5 3B through Ollama |
| Embeddings | all-minilm through Ollama |
| Retrieval | NumPy cosine similarity |
| Validation | Pydantic |
| Knowledge base | Markdown |
| Mock enterprise data | JSON |
| Testing | pytest and custom Python evaluation suite |

The application uses local models and does not require paid external LLM or embedding API calls.

## Project structure

```text
raapid-agentic-assistant/
│
├── app/
│   ├── main.py
│   ├── orchestrator.py
│   ├── router.py
│   ├── schemas.py
│   ├── policy_assistant.py
│   ├── document_loader.py
│   ├── vector_store.py
│   ├── guardrails.py
│   ├── tools.py
│   ├── action_tools.py
│   └── evaluator.py
│
├── knowledge_base/
│   ├── leave_policy_2024.md
│   ├── leave_policy_2026.md
│   ├── expense_policy.md
│   ├── finance_faq.md
│   ├── security_procedure.md
│   ├── onboarding_guide.md
│   ├── asset_policy.md
│   ├── remote_work_policy.md
│   └── travel_policy.md
│
├── data/
│   ├── employees.json
│   ├── leave_balances.json
│   ├── reimbursements.json
│   ├── assets.json
│   ├── tickets.json
│   ├── human_review.json
│   └── knowledge_base_vectors.json
│
├── evals/
│   ├── evaluation_suite.json
│   ├── retrieval_evaluation.json
│   ├── retrieval_results.json
│   ├── performance_results.json
│   ├── baseline_results.json
│   ├── regression_results.json
│   └── final_results.json
│
├── docs/
│   ├── architecture.md
│   ├── failure_log.md
│   └── performance_and_cost.md
│
├── tests/
├── requirements.txt
└── README.md
```

## Prerequisites

- Windows, macOS or Linux.
- Python 3.12 or a compatible Python version.
- Git (optional, for repository management).
- Ollama installed and running.

The prototype was developed and tested locally on Windows with Python 3.15.2.

## Setup instructions

### 1. Clone or download the repository

Open a terminal in the project directory.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the required Ollama models

```bash
ollama pull qwen2.5:3b
ollama pull all-minilm
```

Ensure Ollama is running.

### 5. Build the knowledge-base vector store

```bash
python -m app.vector_store
```

This loads the Markdown knowledge base, generates embeddings and saves the local vector store.

### 6. Launch the application

```bash
streamlit run app/main.py
```

The Streamlit interface should open in your browser.

## Evaluation and testing

### Run the complete evaluation suite

```bash
python -m app.evaluator
```

The evaluator executes 24 scenarios and saves the raw results to:

```text
evals/raw_results.json
```

### Run retrieval quality evaluation

```bash
python -m app.evaluate_retrieval
```

Results are saved to:

```text
evals/retrieval_results.json
```

### Run automated unit tests

```bash
pytest -q
```

### Run performance benchmark

```bash
python -m app.benchmark
```

Results are saved to:

```text
evals/performance_results.json
```

## Evaluation results

Final evaluation of the working implementation:

| Metric | Result |
|---|---:|
| Total scenarios | 24 |
| Passed | 24 |
| Failed | 0 |
| Overall pass rate | 100% |
| Mandatory scenarios | 6/6 |

### Mandatory scenarios covered

1. Superseded policy source handling.
2. Unanswerable question abstention.
3. Conflicting policy sources.
4. Employee entitlement and access boundary.
5. Tool failure and graceful fallback.
6. Ambiguous request clarification.

### Retrieval evaluation

The labelled ten-query retrieval benchmark achieved:

| Metric | Result |
|---|---:|
| Hit Rate@2 | 100% |
| Recall@2 | 100% |
| Precision@2 | 70% |

These results are based on a small prototype dataset.

### Regression experiment

The current-document filter was deliberately disabled to test whether the evaluation suite could detect outdated policy citations.

| Version | Result |
|---|---:|
| Working baseline | 24/24 |
| Deliberately broken version | 23/24 |
| Restored working version | 24/24 |

The superseded-policy scenario detected the incorrect LEAVE-2024 citation.

## Example employee requests

**Policy questions**
- How many annual paid leave days do employees get?
- What is the meal reimbursement limit?
- What should I do if my laptop is stolen?

**Structured record queries**
- What is my leave balance?
- Show my reimbursement status.
- What assets are assigned to me?

**Action requests**
- Raise a ticket for my laptop issue.
- Report a security incident.
- Update my bank details.

The last example is routed to human review rather than being executed automatically.

## Architecture and design documentation

See:

- `docs/architecture.md` — architecture, design decisions, retrieval, orchestration, security, evaluation and limitations.
- `docs/failure_log.md` — development issues, debugging and corrective actions.
- `docs/performance_and_cost.md` — latency measurements, cost assumptions and scaling considerations.

## Important prototype limitations

This is a demonstration prototype, not a production-ready enterprise HR system.

- Employee identity is currently represented by a fixed demo session ID.
- Employee records and action results are stored in local JSON files.
- The human-review workflow creates pending records; it does not provide a full approval application.
- Prompt-injection detection uses phrase-based rules and is not comprehensive.
- The conflict detector currently handles the deliberately seeded meal-limit conflict.
- The retrieval confidence threshold requires broader calibration.
- No concurrent-load or production-scale testing has been conducted.
- Vector-store updates require manual rebuilding.

Production deployment would require enterprise SSO, secure enterprise APIs, transactional storage, stronger authorization and audit controls, monitoring and scalability testing.

## AI tooling disclosure

- ChatGPT was used to assist with architecture design, implementation guidance, code generation and debugging.
- Ollama with Qwen2.5 3B was used as the local runtime LLM.
- The user selected a local-model approach to avoid dependence on hosted-model free-tier quotas.
- The evaluation suite uses deterministic assertions rather than an LLM judge.

All generated implementation components were run and checked against the local prototype and its evaluation scenarios.

## Author

RAAPID Agentic AI Assignment  
Employee AI Assistant Prototype
```

**Important before saving:** This README assumes the filenames shown in the project structure exist. We will verify the actual folder contents and adjust any mismatches during final cleanup.

Save with `Ctrl + S`.

Tell me once you've saved it. Next we'll verify the project files and prepare the final tooling disclosure and submission checklist.