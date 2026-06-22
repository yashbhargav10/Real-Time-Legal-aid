import requests

url = "http://127.0.0.1:8081/query"
payload = {
    "session_id": "test_session_123",
    "query": "tenant security deposit rights"
}
headers = {"X-API-Key": "legalaid-super-secret-key-123"}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
