# 🛡️ Security Model

The Universal LLM Gateway is built with a "Security-First" architecture to protect both the gateway infrastructure and the sensitive data passing through it.

## 1. Authentication Layer

- **API Key Hashing**: We use **Argon2id** (the winner of the Password Hashing Competition) to store API keys. This ensures that even in the event of a database breach, keys cannot be unhashed.
- **Multi-Tenant Isolation**: Every request is scoped to a specific `TenantID`, ensuring that data, budgets, and rate limits never leak across organizational boundaries.

## 2. Dynamic Guardrails

### Prompt Injection Mitigation

The gateway monitors incoming messages for known injection patterns using high-performance regex scanning.

- **Pattern Matching**: Detects "Ignore previous instructions", "DAN" mode attempts, and prompt leakage probes.
- **Action**: Violating requests are blocked with a `403 Forbidden` before reaching the LLM provider.

### PII Redaction

Our `PIIRedactor` service masks sensitive information (Emails, SSNs, Credit Cards) in the request logs.

- **Logic**: Redaction is performed using a high-throughput pattern-matching pipeline.
- **Compliance**: Ensures that sensitive user data is never persisted in our historical logs.

## 3. Resilience & Defense-in-Depth

- **Distributed Circuit Breaker**: We use Redis to maintain global circuit states. If a provider (e.g., Anthropic) starts failing >50% of requests, our gateway automatically opens the circuit to prevent cascading failures.
- **Brute Force Protection**: Repeated failed auth attempts from the same IP or account trigger an automatic cooldown period.
- **Rate Limiting**: Distributed Token Bucket algorithm prevents DoS attacks and manages fair usage.

## 4. Logging & Audit

- **Immutable Request Logs**: Every request is logged with a unique `X-Request-ID`.
- **Sanitization**: All logged payloads are sanitized and redacted before storage in PostgreSQL.
- **Archival**: Old logs are moved to encrypted S3 buckets for long-term compliance storage.

## 📡 Security Headers

The gateway injects standard protection headers into every response:

- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy` (CSP)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
