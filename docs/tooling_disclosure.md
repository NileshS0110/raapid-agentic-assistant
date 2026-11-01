\# AI Tooling Disclosure

\## Employee AI Assistant – RAAPID Assignment



\### 1. Tools and Technologies Used



| Tool / Technology | Purpose |

|---|---|

| Python | Application logic, orchestration and evaluation |

| Streamlit | Employee-facing application interface |

| Ollama | Local LLM and embedding model runtime |

| Qwen2.5 3B | Policy answer generation |

| all-minilm | Local document and query embeddings |

| NumPy | Cosine similarity and vector retrieval |

| Pydantic | Input and output schema validation |

| Pytest | Automated unit testing |

| JSON | Mock employee records, tickets and vector-store persistence |

| Git / GitHub Desktop | Source-code version control |

| ChatGPT | Architecture planning, implementation guidance, code generation, debugging and documentation assistance |



\### 2. AI-Assisted Development



ChatGPT assisted with:

\- Designing the overall application architecture.

\- Defining deterministic routing and workflow branches.

\- Generating initial Python implementation code.

\- Designing Pydantic request and response schemas.

\- Implementing document loading, chunking and vector retrieval.

\- Designing guardrails and human-review workflows.

\- Creating evaluation scenarios and deterministic assertions.

\- Debugging implementation and test failures.

\- Preparing architecture, failure-log and README documentation.



Ollama was used to run Qwen2.5 3B locally for policy response generation. The all-minilm model was used for document and query embeddings.



Generated code was reviewed, executed and tested locally. Implementation decisions and corrections were made based on observed behaviour, test failures and evaluation results.



\### 3. Important Implementation Decisions



The following design requirements and decisions were explicitly selected:



\- Three request categories: policy questions, structured record queries and action requests.

\- Deterministic Python routing rather than unrestricted LLM-based routing.

\- A lightweight custom retrieval pipeline instead of a large agent framework.

\- Local Ollama models to avoid dependence on paid hosted-model APIs and free-tier quotas.

\- Current-versus-superseded policy filtering.

\- Employee-level access checks.

\- Explicit human review for sensitive actions.

\- Mock JSON data instead of connecting to real HR systems.

\- Deterministic evaluation rather than relying on an LLM judge.

\- A deliberately introduced regression to validate evaluation effectiveness.



\### 4. Important Design Override



An important architectural decision was to avoid introducing a multi-agent framework such as LangChain agents, CrewAI or LangGraph.



Although agent frameworks could have been used, a simpler Python orchestrator was selected because:



\- The assignment required explicit multi-step branching and tool execution, not necessarily multiple autonomous agents.

\- Deterministic routing and business rules are easier to inspect and test.

\- A lightweight implementation reduces dependencies and local setup complexity.

\- It makes failure handling, authorization and evaluation easier to demonstrate.



A second important choice was to use Qwen2.5 3B through Ollama instead of depending on a hosted LLM free tier.



\### 5. Example of Human Correction / Override



The initial routing logic incorrectly classified a request such as "Raise a ticket for my laptop issue" as an asset-record query because it matched the phrase "my laptop".



This was identified through end-to-end evaluation failures affecting ticket creation and tool-failure scenarios.



The multiple-intent and action-detection rules were refined to distinguish an explicit ticket-creation request from an actual asset-record lookup.



The correction was verified through automated tests and the evaluation suite.



Other corrections made during development included:

\- Adding missing routing keywords after a test failure.

\- Separating short-input validation from clarification handling.

\- Correcting Windows document encoding issues.

\- Refining multiple-intent detection.

\- Restoring the superseded-document filter after the evaluation suite detected its removal.



\### 6. Human Validation and Evaluation



Implementation was validated through:

\- Local execution of the Streamlit application.

\- Individual module tests.

\- Automated evaluation of 24 scenarios.

\- A ten-query retrieval-quality benchmark.

\- End-to-end latency measurements.

\- A deliberate regression experiment.



The final evaluation uses deterministic assertions rather than an LLM-as-a-judge approach. This avoids the need for model-judge calibration and manual agreement calculations.



Final evaluation:

\- 24 of 24 scenarios passed.

\- All six mandatory scenarios passed.

\- A deliberately introduced regression caused one scenario to fail.

\- Restoring the original implementation returned the suite to 24 of 24 passing scenarios.



\### 7. Scope and Limitations



This is a prototype built with mock employee data and local models. It does not connect to production HR, finance, identity or ticketing systems.



No real employee records or credentials were used.



AI-assisted code generation does not replace engineering validation. The prototype has been tested against its defined scenarios, but it has not undergone enterprise security certification, production-scale load testing or independent security review.



Local execution avoids external inference API charges, but does not eliminate hardware, electricity or maintenance costs.



The implementation should therefore be treated as a working assignment prototype rather than a production-ready enterprise application.

