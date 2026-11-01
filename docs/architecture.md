\# Employee AI Assistant — Architecture Note



\## 1. Overview



The Employee AI Assistant handles three request categories:

\- Policy and process questions using an internal knowledge base.

\- Structured employee record queries such as leave, reimbursements and assets.

\- Action requests such as ticket creation and requests requiring human approval.



The prototype uses Python, Streamlit, Ollama with Qwen 2.5 3B, local embeddings, JSON mock data and Pydantic response validation.



\## 2. Architecture and request flow



1\. Streamlit collects the employee request.

2\. Pydantic validates the input.

3\. A deterministic Python router classifies the request.

4\. The orchestrator applies security, ambiguity and multi-intent checks.

5\. The request is directed to the relevant workflow:

&#x20;  - Policy: retrieve relevant knowledge-base chunks and generate a grounded answer.

&#x20;  - Record: call structured JSON-backed tools.

&#x20;  - Action: create a ticket or submit the request for human review.

6\. The orchestrator returns a structured response.

7\. Streamlit displays the answer, citations, tool activity and status.



The router uses deterministic keyword and rule-based decisions rather than relying entirely on an LLM.



\## 3. Retrieval and knowledge base



The knowledge base contains nine Markdown documents covering leave, expenses, finance FAQs, security, onboarding, assets, remote work and travel.



\- Chunking: 180 words per chunk, with 30-word overlap.

\- Embeddings: Ollama `all-minilm`, 384-dimensional vectors.

\- Retrieval: cosine similarity using NumPy.

\- Retrieval depth: top 2 chunks.

\- Version handling: documents marked superseded are filtered before ranking.

\- Context limit: 300 words.

\- Confidence threshold: 0.30; this is provisional and requires broader calibration.



The evaluation set contains 10 manually labelled retrieval queries. At k=2, hit rate and recall are 100%, while precision is 70%. This is a small prototype benchmark, not a production-scale quality estimate.



A seeded conflict between the expense policy and finance FAQ is surfaced to the user rather than silently resolved.



\## 4. Structured tools, security and human review



Structured tools retrieve leave balances, reimbursement status and assigned assets from mock JSON records. At least two structured tool integrations are exercised.



The prototype checks that the requested employee matches the demo session employee. Cross-employee and unauthenticated requests are denied.



Ticket creation validates required fields and priority, uses request IDs to prevent duplicate creation, and handles simulated tool failures.



Sensitive actions, such as changing bank details, are routed to a pending human-review queue rather than executed automatically.



The demo employee identity is hard-coded. A production system must derive identity from trusted SSO/JWT authentication and enforce authorization at the service layer.



\## 5. Evaluation and results



The evaluation suite contains 24 scenarios and uses deterministic assertions. No LLM judge is used.



The suite covers:

\- Superseded policy handling.

\- Unanswerable questions and abstention.

\- Conflicting sources.

\- Employee entitlement boundaries.

\- Tool failure and graceful fallback.

\- Ambiguous requests and clarification.

\- Additional security, validation and action failure cases.



Final evaluation: 24/24 passed, including all 6 mandatory situations.



A deliberate regression disabled the superseded-document filter. The suite then fell to 23/24: the superseded-policy test failed. Restoring the filter returned the result to 24/24.



\## 6. Performance, cost and limitations



Measured median end-to-end latency:

\- Policy question: approximately 6.08 seconds.

\- Structured record query: approximately 0.58 milliseconds.

\- Ticket creation: approximately 9.28 milliseconds.



These measurements use five sequential runs per workflow and do not represent concurrent-load performance.



External API cost is zero in this local prototype because inference, embeddings and storage run locally. Electricity, hardware and maintenance costs are excluded.



Key limitations include small evaluation datasets, provisional retrieval threshold, local-model latency, JSON storage, fixed demo identity and limited concurrency. Production deployment would require SSO, persistent databases, monitoring, broader evaluations, load testing and stronger policy conflict governance.

