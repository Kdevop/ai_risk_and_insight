import requests

r = requests.post(
    "http://127.0.0.1:8000/agent",
    json={"message": "hello agent"}
)

print(r.json())