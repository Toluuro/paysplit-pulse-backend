import requests

# 1. Point the URL to your live Render server instead of localhost
url = "https://paysplit-pulse-api.onrender.com/api/webhooks/settle/"

# 2. Pack the JSON payload with your new Database IDs
payload = {
    "transaction_id": "TSW-WEBHOOK-LIVE-001", # Unique ID for this test
    "amount": "100000.00",
    "rule_id": 2,             # Your active Split Rule ID
    "primary_vendor_id": 2    # Your active Vendor ID
}

print(f"Sending webhook for {payload['transaction_id']} to production...")

# Fire the POST request across the internet
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")