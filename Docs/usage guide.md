# 🚀 Usage Guide

This guide covers how to interact with the Universal LLM Gateway using standard tools like `curl` and Python.

## 🔑 Authentication

Every request must include your gateway API key in the `Authorization` header.

```bash
curl -H "Authorization: Bearer <YOUR_GATEWAY_KEY>" http://localhost:8000/v1/chat/completions ...
```

---

## 💬 Basic Completion

The gateway mimics the OpenAI API format for seamless integration.

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "How does semantic caching work?"}]
  }'
```

---

## 🏁 Model Racing (Ensembling)

To get the fastest possible response, you can "race" multiple providers using a custom header.

```bash
curl http://localhost:8000/v1/chat/completions ... \
  -H "X-Model-Race: true" \
  -d '{
    "model": "auto",
    "messages": [...]
  }'
```

*Note: The gateway will call both OpenAI and Anthropic; the first to respond will be used.*

---

## 🧠 Semantic Cache Control

You can force the gateway to ignore the cache or check the cache status in the response.

- **Bypass Cache**: Send `X-Cache-Bypass: true`.
- **Check Status**: Look for the `X-Cache-Status` header in the response (`HIT` or `MISS`).

---

## 📈 Monitoring Usage

Tenant admins can check their remaining budget and usage via the admin API.

```bash
curl http://localhost:8000/admin/analytics \
  -H "X-Admin-Token: <ADMIN_SECRET>"
```
