# 🏗️ Architectural Overview

The Universal LLM Gateway is designed for high-throughput, low-latency LLM orchestration with an emphasis on enterprise security and observability.

## 📐 Layered Architecture

The system is composed of five distinct layers:

1. **Ingress Layer**: FastAPI routes, standardizing OpenAI-compatible requests.
2. **Guardrail Layer**: Auth middleware, rate limiting, and prompt safety scrubbing.
3. **Intelligence Layer**: Semantic caching and the routing engine.
4. **Adapter Layer**: Provider-specific logic (OpenAI, Anthropic, Bedrock) with circuit breakers.
5. **Observability Layer**: Prometheus metrics, OpenTelemetry tracing, and structured logging.

---

## 🔄 Request Lifecycle (Sequence Diagrams)

### 1. Standard Request Flow

This diagram illustrates the standard path for a non-cached completion request.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth/Security
    participant R as Router
    participant P as Provider (OAI/ANT)
    participant L as Logger
    
    C->>A: POST /v1/chat/completions (with API Key)
    A->>A: Validate Key & Rate Limits
    A->>R: Forward Authorized Request
    R->>R: Select Best Model/Provider
    R->>P: Dispatch Request
    P-->>R: LLM Response (JSON or Stream)
    R->>L: Record Tokens & Cost
    R-->>C: Standardized Response
```

### 2. Semantic Cache Flow

How the gateway recovers responses from the vector database without calling the LLM provider.

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Cache Manager
    participant V as RediSearch (Vector DB)
    participant P as Provider
    
    C->>M: Completion Request
    M->>M: Generate Embedding for Prompt
    M->>V: KNN Similarity Search (Threshold 0.95)
    alt Cache Hit
        V-->>M: Return Cached Result
        M-->>C: 200 OK (X-Cache: HIT)
    else Cache Miss
        V-->>M: No near match
        M->>P: Call Provider
        P-->>M: Response
        M->>V: Store Response & Embedding
        M-->>C: 200 OK (X-Cache: MISS)
    end
```

### 3. Model Ensembling (Race Flow)

This illustrates the "Fastest Wins" logic used for ultra-low latency requirements.

```mermaid
sequenceDiagram
    participant G as Gateway Ensembler
    participant P1 as Provider 1 (GPT-4o)
    participant P2 as Provider 2 (Claude 3.5)
    
    G->>P1: Request (Async Task)
    G->>P2: Request (Async Task)
    Note over G: Wait for first to complete
    P2-->>G: Returns Result (Ha Ha, I won!)
    G-->>G: Cancel Task P1
    G-->>Client: Return P2 Response
```

---

## 🛠️ Component Interactions

- **Redis**: Acts as the ephemeral storage for rate limit buckets, exact-match caching, and distributed circuit breaker states.
- **RediSearch**: Extends Redis with vector indexing for semantic similarity search.
- **PostgreSQL**: Stores persistent data: API keys, tenant budgets, and historical request logs.
- **OpenTelemetry**: Proxies tracing spans to Jaeger or Zipkin for cross-service observability.
