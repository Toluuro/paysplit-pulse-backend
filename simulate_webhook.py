import requests

# The API endpoint you just built
url = "http://127.0.0.1:8000/api/webhooks/settle/"

# The payload representing a $150,000 successful property purchase
payload = {
    "transaction_id": "TSW-WEBHOOK-003",
    "amount": "1200000.00",
    "rule_id": 1,
    "primary_vendor_id": 1,
    "agent_id": 2
}

print(f"Sending webhook for {payload['transaction_id']}...")

# Fire the POST request
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")