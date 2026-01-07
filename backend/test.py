import requests

url = "http://localhost:5000/api/ai"
payload = {
    "text": "oi"
}

response = requests.post(url, json=payload)

print(response.json())