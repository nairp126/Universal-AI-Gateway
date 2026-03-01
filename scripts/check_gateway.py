import requests
import json
import time

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "CHANGE_ME_ADMIN_TOKEN" # from .env or k8s secret

def print_step(title):
    print(f"\n{'='*50}")
    print(f"🚀 TEST: {title}")
    print(f"{'='*50}")

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# 1. Health & Dependency Check
print_step("Health Check (Postgres, Redis, Providers)")
resp = requests.get(f"{BASE_URL}/health")
print_response(resp)

# 2. Chat Completions - Normal (Will return 4xx from provider without keys, but routing works)
print_step("Chat Completion Routing (OpenAI GPT-4o proxy)")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer fake_key_for_testing"
}
payload = {
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
}
start = time.time()
resp = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
duration = time.time() - start
print(f"Time taken: {duration:.2f}s")
print_response(resp)

# 3. Test Caching (Request identical payload)
print_step("Caching mechanism (Identical payload)")
start = time.time()
resp2 = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
duration2 = time.time() - start
print(f"Time taken: {duration2:.2f}s")
if "x-cache" in resp2.headers:
    print(f"✅ Cache Hit! Header X-Cache: {resp2.headers['x-cache']}")
print_response(resp2)

# 4. Admin Analytics (Requires Auth)
print_step("Admin Analytics (Without Token - Should Fail)")
resp_auth_fail = requests.get(f"{BASE_URL}/admin/analytics")
print(f"Status: {resp_auth_fail.status_code}")

print_step("Admin Analytics (With Token - Should Succeed)")
resp_auth_success = requests.get(f"{BASE_URL}/admin/analytics", headers={"X-Admin-Token": "test_admin_key_12345"})
print_response(resp_auth_success)

# 5. Rate Limiting Tests
print_step("Rate Limiting (Spam requests)")
print("Sending 65 rapid requests to trigger limiters...")
for i in range(1, 66):
    res = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
    if res.status_code == 429:
        print(f"Request {i}: 🔴 RATELIMIT HIT (429)")
        break
    elif res.status_code != 200:
        print(f"Request {i}: Failed {res.status_code}")
    else:
        print(f"Request {i+1}: 🟢 200 OK")
