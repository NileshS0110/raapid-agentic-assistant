\# Employee AI Assistant — Architecture Note



\## 1. Overview



The Employee AI Assistant handles three request categories:



\- Policy and process questions using an internal knowledge base.

\- Structured employee record queries such as leave, reimbursements and assets.

\- Action requests such as ticket creation and requests requiring human approval.



The prototype uses Python, Streamlit, Ollama with Qwen 2.5 3B, local embeddings, JSON mock data and Pydantic response validation.



\## 2. Architecture and Request Flow



1\. Streamlit collects the employee request.

2\. Pydantic validates the input.

3\. A deterministic Python router classifies the request.

4\. The orchestrator applies security, ambiguity and multi-intent checks.

5\. The request is directed to the relevant workflow:

&#x20;  - \*\*Policy:\*\* Retrieve relevant knowledge-base chunks and generate a grounded answer.

&#x20;  - \*\*Record:\*\* Call structured JSON-backed tools.

&#x20;  - \*\*Action:\*\* Create a ticket or submit the request for human review.

6\. The orchestrator returns a structured response.

7\. Streamlit displays the answer, citations, tool activity and status.



The router uses deterministic keyword and rule-based decisions rather than relying entirely on an LLM.



\## 3. Retrieval and Knowledge Base



The knowledge base contains nine Markdown documents covering leave, expenses, finance, security, onboarding, assets, remote work and travel.



\- Chunking: 180 words per chunk, with 30-word overlap.

\- Embeddings: Ollama `all-minilm`, 384-dimensional vectors.

\- Retrieval: Cosine similarity using NumPy.

\- Retrieval depth: Top 2 chunks.

\- Version handling: Documents marked superseded are filtered before ranking.

\- Context limit: 300 words.

\- Confidence threshold: 0.30; provisional and requiring broader calibration.



The evaluation set contains 10 manually labelled retrieval queries. At k=2, hit rate and recall are 100%, while precision is 70%.



A seeded conflict between the expense policy and finance FAQ is surfaced to the user rather than silently resolved.



\## 4. Structured Tools, Security and Human Review



Structured tools retrieve leave balances, reimbursement status and assigned assets from mock JSON records. Additional tools support IT ticket creation and human-review submission.



Security controls include:



\- Employee-level authorization checks.

\- Cross-employee access prevention.

\- Input and priority validation.

\- Duplicate ticket prevention using request IDs.

\- Graceful tool-failure handling.

\- Human review for sensitive actions.



Sensitive actions, such as changing bank details, are routed to a pending human-review queue rather than executed automatically.



The demo employee identity is hard-coded. A production system must derive identity from trusted SSO/JWT authentication and enforce authorization at the service layer.





\## 5. Evaluation and Acceptance



The system is evaluated using 24 deterministic test scenarios. No LLM-as-judge is used.



\*\*Predefined acceptance thresholds\*\* are stored in `evals/evaluation\_thresholds.json` and enforced by the evaluator:



\- Overall pass rate: at least 90%.

\- Mandatory scenarios: 100%.

\- Critical security scenarios: 100%.



\*\*Final results:\*\*

\- Overall: 24/24 passed (100%).

\- Mandatory situations: 6/6 passed (100%).

\- Critical security scenarios: 5/5 passed (100%).

\- All acceptance thresholds passed.



A deliberate regression test disabled the current-document version filter. The suite detected the issue: 23/24 scenarios passed, with superseded-policy scenario E02 failing. After restoring the filter, the suite returned to 24/24.



Detailed scenario results, thresholds, retrieval metrics and regression evidence are available in the `evals/` directory.



The evaluation suite contains 24 scenarios and uses deterministic assertions. No LLM judge is used.



The suite covers:



\- Superseded policy handling.

\- Unanswerable questions and abstention.

\- Conflicting sources.

\- Employee entitlement boundaries.

\- Tool failure and graceful fallback.

\- Ambiguous requests and clarification.

\- Additional security, validation and action failure cases.



Final evaluation: \*\*24/24 passed (100%)\*\*, including all six mandatory situations.



A deliberate regression disabled the superseded-document filter. The suite then fell to 23/24: the superseded-policy test failed because the old policy could be cited. Restoring the filter returned the result to 24/24.



\## 6. Performance, Cost and Limitations



Observed median end-to-end latency, based on five sequential runs per workflow:



\- Policy question: approximately 6.08 seconds.

\- Structured record query: approximately 0.58 milliseconds.

\- Ticket creation: approximately 9.28 milliseconds.



External API cost is zero in this local prototype because inference, embeddings and storage run locally. Electricity, hardware and maintenance costs are excluded.



Key limitations include:



\- Small knowledge base and evaluation datasets.

\- Provisional retrieval confidence threshold.

\- Local-model inference latency.

\- JSON storage rather than production transactional databases.

\- Fixed demo employee identity.

\- Seeded conflict detection rather than generalized contradiction detection.

\- No concurrent-load or production-scale testing.

\- Manual vector-store rebuilding.



Production improvements would include enterprise SSO, authenticated HR integrations, scalable storage, broader evaluation datasets, automated document version management, monitoring and a proper human-approval interface.

