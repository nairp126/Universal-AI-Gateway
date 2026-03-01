# 🚀 Enterprise Features

The Universal LLM Gateway provides a suite of advanced features designed to optimize cost, latency, and security for large-scale AI deployments.

---

## 🧠 Semantic Caching

Unlike exact-match caching, semantic caching identifies prompts that are conceptually similar, even if they aren't identical.

- **Vectorization**: Uses OpenAI `text-embedding-3-small` to convert prompts into 1536-dimensional vectors.
- **Search**: Leverages **RediSearch** (KNN similarity search) with an HNSW index for ultra-fast retrieval (<50ms).
- **Threshold**: Configurable similarity (defaults to 0.95 cosine similarity).
- **Efficiency**: Reduces redundant LLM calls by up to 80% for common Q&A workloads.

## 🏁 Model Ensembling (Racing)

Achieve the lowest possible latency and highest availability by racing multiple models concurrently.

- **Fastest Wins**: The gateway dispatches the same request to multiple providers (e.g., OpenAI and Claude) and returns the first successful response to the client.
- **Async Efficiency**: Uses `asyncio.as_completed` to minimize idle wait time.
- **Reliability**: If one provider is slow or experiencing a partial outage, the other fulfills the request.

## 💰 Financial Guardrails & Budgeting

Manage AI spend with precision across teams and projects.

- **Atomic Tracking**: Uses Redis `INCRBYFLOAT` for race-condition-free cost tracking.
- **Daily Caps**: Set mandatory USD budget limits per tenant.
- **Real-time Rejection**: Requests are blocked immediately once a tenant's daily limit is hit, returning a `402 Payment Required`.

## 🛡️ Content Safety & Guardrails

- **Regex Protection**: Real-time scanning for prompt injections and malicious system instructions.
- **PII Redaction**: Multi-step regex pipeline to mask emails, phone numbers, and SSNs in historical logs.
- **Circuit Breakers**: standard state-machine logic to isolate failing models and prevent cascading failures.
