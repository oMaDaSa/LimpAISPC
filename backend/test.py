import requests

import requests
import os

API_KEY = os.getenv("GOOGLE_API_KEY")

url = "http://localhost:5000/api/ai"
payload = {
    "text": "Qual o Art. 5º da Lei do Superendividamento?"
}

response = requests.post(url, json=payload)

print(response.json())