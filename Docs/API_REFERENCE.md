# 📖 API Reference

Comprehensive specification for the Universal LLM Gateway API.

## 🟢 Public Endpoints

### Post Chat Completion

`POST /v1/chat/completions`

OpenAI-compatible chat completion endpoint.

**Request Body** (Selected Fields):

- `model` (string, required): The ID of the model to use. Use `auto` for gateway default.
- `messages` (array, required): List of message objects.
- `stream` (boolean): If true, returns SSE stream.
- `temperature` (float): Sampling temperature (0-2).
- `max_tokens` (integer): Maximum tokens to generate.

**Custom Gateway Headers**:

- `X-Model-Race`: (boolean) Enable concurrent racing between providers.
- `X-Cache-Bypass`: (boolean) Force miss and refresh cache.

**Response Headers**:

- `X-Request-ID`: Correlation ID for debugging.
- `X-Cache-Status`: `HIT` | `MISS` | `BYPASS`.
- `X-Tenant-Budget-Remaining`: Remaining USD budget for the tenant.
- `X-Provider`: The actual provider that served the request (e.g., `anthropic`).

---

## 🛠️ Admin Endpoints

*Requires `X-Admin-Token` authentication.*

### List API Keys

`GET /admin/api-keys`

- Lists all active keys, scopes, and associated tenants.

### Usage Analytics

`GET /admin/analytics`

- Returns system-wide token usage, cache hit rate, and cost aggregation.

### Export Logs

`POST /admin/logs/export`

- Triggers an archival job to move older request logs to S3.

---

## 🛑 Error Codes

| Status | Code | Meaning |
| :--- | :--- | :--- |
| 401 | `invalid_api_key` | API key is missing or invalid. |
| 402 | `budget_exceeded` | Tenant has exceeded their daily USD spend limit. |
| 403 | `safety_violation` | Prompt contains malicious injection or unsafe content. |
| 429 | `rate_limit_exceeded` | Too many requests for this key/tenant. |
| 502 | `provider_error` | Downstream provider returned an error. |
| 503 | `circuit_breaker_open` | Provider is temporarily isolated due to failure rate. |
