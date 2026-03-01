# 🗺️ Codebase Map

A technical directory of the Universal LLM Gateway codebase to assist developers in navigating the architecture and implementation details.

## 📂 `app/` - Core Application Logic

| File/Directory | Responsibility | Technical Implementation |
| :--- | :--- | :--- |
| `main.py` | App Entrypoint | FastAPI application factory, middleware wiring. |
| `api/` | Route Handlers | `/v1/chat/completions`, `/health`, `/admin` endpoints. |
| `middleware/` | Ingress Filters | Auth, Rate Limiting, Security Headers, Error Handling. |
| `services/` | Business Logic | Router, Ensembler, Budget Manager, PII Redactor. |
| `providers/` | Adapter Layer | OpenAI, Anthropic, Bedrock adapters; Circuit Breaker. |
| `cache/` | Caching Logic | Redis exact-match and RediSearch semantic caching. |
| `db/` | Persistence | SQLAlchemy models and database connection manager. |
| `schemas/` | Validation | Pydantic models for request/response validation. |
| `core/` | Infrastructure | Configuration (Pydantic Settings), Logging, Security. |

---

## 📂 `tests/` - Quality Assurance

| File | Category | Description |
| :--- | :--- | :--- |
| `test_api.py` | Integration | End-to-end API lifecycle testing. |
| `test_auth.py` | Security | API key validation and Argon2id verification. |
| `test_providers.py` | Logic | Comprehensive adapter and circuit breaker unit tests. |
| `test_gateway_features.py` | Functional | Verification of cache, routing, and enterprise features. |
| `conftest.py` | Fixtures | Shared test dependencies and mock configurations. |

---

## 📂 `root/` - Infrastructure & Governance

| File/Directory | Purpose |
| :--- | :--- |
| `Dockerfile` | Multi-stage build for production-ready containerization. |
| `docker-compose.yml` | Local orchestration (Gateway, Postgres, Redis, RediSearch). |
| `alembic.ini` | Database migration configuration. |
| `requirements.txt` | Core application dependencies. |
| `run.py` | Development server startup script. |
| `LICENSE` | Apache License 2.0. |
| `CODE_OF_CONDUCT.md` | Community standards and ethical guidelines. |
| `CONTRIBUTING.md` | Setup and pull request instructions for developers. |
| `docs/` | Comprehensive technical documentation hub. |
| `k8s/` | Kubernetes manifests for production deployment. |
| `monitoring/` | Monitoring configurations (OpenTelemetry, metrics). |
| `scripts/` | Miscellaneous utility and maintenance scripts. |
| `migrations/` | Database version control (Alembic). |
