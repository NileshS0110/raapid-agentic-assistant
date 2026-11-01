

\# Performance and Cost Analysis



\## 1. Measurement Method



Performance was measured using a local Python benchmark that invoked the application's main orchestrator.



\- Five runs per workflow.

\- End-to-end request latency measured using Python's time.perf\_counter().

\- Median, best-case and worst-case latency calculated.

\- All 15 benchmark executions returned successful responses.

\- Environment: local Windows machine, 16 GB RAM, Ollama, Qwen 2.5 3B and all-MiniLM embeddings.



These are prototype development-machine measurements, not production load-test results.



\## 2. Measured Performance



| Workflow | Median | Best case | Worst case |

|---|---:|---:|---:|

| Policy RAG | 6076.59 ms | 6073.03 ms | 6271.66 ms |

| Structured record query | 0.58 ms | 0.50 ms | 0.91 ms |

| Ticket creation | 9.28 ms | 2.67 ms | 14.63 ms |



Policy requests are significantly slower because they include embedding retrieval and local LLM generation.



Structured record queries and ticket creation use deterministic Python workflows and local JSON files, without LLM generation.



\## 3. Cost Analysis



The prototype uses locally hosted Ollama models.



\- LLM API charges: ₹0.

\- Embedding API charges: ₹0.

\- Managed vector database charges: ₹0.

\- Cloud hosting charges: ₹0.



Electricity, hardware depreciation, maintenance and future hosting costs are not included. Therefore, the prototype has zero external API charges, not zero total operating cost.



\## 4. 100x Workload Estimate



Assuming sequential execution on the same machine and using measured median latency:



| Workflow | Estimated time for 100 requests |

|---|---:|

| Policy RAG | 10.13 minutes |

| Structured record query | 58 milliseconds |

| Ticket creation | 0.93 seconds |



These are arithmetic workload estimates, not measured throughput or concurrent-user capacity.



At higher volumes, local LLM inference is expected to become the primary bottleneck. Memory constraints, model contention and request queuing could increase latency.



\## 5. Scaling Improvements



1\. Optimize model inference and evaluate smaller or quantized models.

2\. Introduce controlled concurrency and request queuing.

3\. Cache embeddings and re-embed only modified documents.

4\. Replace JSON files with a transactional database.

5\. Separate the application layer from model inference.

6\. Conduct concurrent load tests before production deployment.



\## 6. Limitations



\- Only five runs per workflow.

\- Measurements taken on one local development machine.

\- No concurrent load testing.

\- No direct measurement of electricity consumption.

\- No separate timing of embedding, retrieval and generation stages.

\- 100x estimates assume sequential execution and unchanged per-request latency.



