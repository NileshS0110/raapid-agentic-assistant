\# Tooling Disclosure — Employee AI Assistant



\## 1. Tools and technologies used



| Tool / Technology | Purpose |

|---|---|

| Python | Application logic, orchestration and evaluation |

| Streamlit | Employee-facing prototype UI |

| Ollama | Local LLM and embedding model execution |

| Qwen 2.5 3B | Policy answer generation and language understanding |

| all-minilm | Local text embeddings |

| NumPy | Cosine similarity and vector retrieval |

| Pydantic | Input and output schema validation |

| Pytest | Automated tests |

| JSON | Mock employee records, tickets and vector-store persistence |

| Git / GitHub Desktop | Source-code version control |

| ChatGPT | Architecture discussion, implementation guidance, debugging and documentation assistance |



\## 2. AI-assisted development



ChatGPT was used to help design the architecture, generate initial code drafts, explain implementation steps, debug errors, create test scenarios and prepare documentation.



Ollama was used to run Qwen 2.5 3B locally for policy response generation. The all-minilm model was used for embeddings.



Generated code was reviewed, executed and tested locally. Implementation decisions and corrections were made based on observed behaviour and test results.



\## 3. Important implementation decisions



\- Used a deterministic Python router rather than delegating all routing decisions to an LLM.

\- Used a lightweight custom retrieval pipeline instead of a large agent framework.

\- Used local Ollama models to avoid dependence on paid external LLM APIs and free-tier quotas.

\- Used mock JSON data instead of connecting to real HR systems.

\- Used deterministic evaluation assertions rather than an LLM judge.

\- Added explicit human review for sensitive actions.



\## 4. Example of a human correction / override



The initial routing logic incorrectly classified "Raise a ticket for my laptop issue" as an asset-record query because it matched laptop-related keywords.



The routing logic was refined to prioritize the user's intended action. The correction was verified through the automated test suite.



\## 5. Scope and limitations



This is a prototype built with mock employee data and local models. It does not connect to production HR, finance, identity or ticketing systems.



No real employee records or credentials were used. Local execution avoids external inference API charges, but does not eliminate hardware, electricity or maintenance costs.

