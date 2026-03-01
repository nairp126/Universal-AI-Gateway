# 🛠️ Development Guide

Welcome to the development guide for the Universal LLM Gateway. This document details how to set up, test, and contribute to the project.

## ⚙️ Local Setup

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (included in compose)
- PostgreSQL (included in compose)

### 2. Environment Configuration

Copy the template and fill in your API keys:

```bash
cp .env.example .env
```

### 3. Start Development Services

Use Docker Compose to spin up the database, Redis, and Jaeger:

```bash
docker-compose up -d
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 🧪 Testing Strategy

We use `pytest` for all unit and integration tests.

- **Run all tests**: `pytest`
- **Run with coverage**: `pytest --cov=app`
- **Integration tests**: `pytest tests/test_integration.py`

### Testing Multi-Provider Race

To test the racing logic without hitting real APIs, set `MOCK_LLM=true` in your `.env`.

---

## 🏗️ Contribution Workflow

1. **Branching**: Create a feature branch from `main` (e.g., `feature/awesome-new-routing`).
2. **Linting**: Ensure code follows PEP 8.
3. **Tests**: All 125+ existing tests must pass before submitting a PR.
4. **Docs**: Update the relevant `docs/` files if your change modifies API behavior or architecture.
