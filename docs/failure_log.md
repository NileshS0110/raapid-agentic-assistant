\# Failure Log — Employee AI Assistant



This log records implementation failures, how they were identified, and the corrective actions taken.



\## 1. Router did not recognize a short leave query



\*\*What happened:\*\* The deterministic router did not classify "leave days" correctly as a record query.



\*\*How it was found:\*\* A router test failed for this phrase.



\*\*What changed:\*\* Updated the routing keyword rules to recognize leave-related record queries.



\*\*Learning:\*\* Real employee requests are often short and informal. Router coverage needs to include natural variations, not just idealized phrases.



\## 2. Short greetings failed input validation



\*\*What happened:\*\* Pydantic rejected a short input such as "Hi" before the router could return a clarification response.



\*\*How it was found:\*\* A test expecting a clarification route failed.



\*\*What changed:\*\* Adjusted the minimum input validation so short messages can reach the deterministic clarification logic.



\*\*Learning:\*\* Input validation should reject genuinely invalid input without blocking requests that the assistant can clarify.



\## 3. Knowledge-base document encoding error



\*\*What happened:\*\* The document loader raised a UnicodeDecodeError when reading Markdown files created through Windows PowerShell.



\*\*How it was found:\*\* The retrieval pipeline failed while loading the knowledge base.



\*\*What changed:\*\* Updated the document loader to read the files using CP1252 encoding.



\*\*Learning:\*\* File encoding should be explicit and consistent across document creation and ingestion.



\## 4. Multi-intent detection incorrectly classified a ticket request



\*\*What happened:\*\* A request such as "Raise a ticket for my laptop issue" was incorrectly treated as a structured asset-record query because of the phrase "my laptop".



\*\*How it was found:\*\* An end-to-end test exposed the incorrect routing.



\*\*What changed:\*\* Refined the deterministic multi-intent and action detection rules so ticket-creation language is not incorrectly overridden by asset-related keywords.



\*\*Learning:\*\* Routing rules must consider the user's intended action, not just isolated keywords.



\## 5. Deliberate regression: superseded policy filter disabled



\*\*What happened:\*\* The current-versus-superseded document filter was deliberately disabled in the retrieval code.



\*\*How it was found:\*\* The 24-scenario evaluation suite was rerun.



\*\*Result:\*\* The suite dropped from 24/24 to 23/24. Scenario E02 failed because the superseded 2024 leave policy could be cited.



\*\*What changed:\*\* Restored the superseded-document filter and reran the evaluation suite.



\*\*Final result:\*\* 24/24 scenarios passed again, including all six mandatory scenarios.



\*\*Learning:\*\* Regression tests are essential for protecting policy-version handling. A seemingly small retrieval change can cause an outdated policy to be presented as current.

