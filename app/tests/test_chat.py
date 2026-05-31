import requests
import json

FLASK_URL = "http://127.0.0.1:5000/chat"

def test_chat():
    payload = {"message": "hello from test file"}

    print("Sending payload:", payload)

    response = requests.post(
        FLASK_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print("Status code:", response.status_code)

    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Raw response text:", response.text)

if __name__ == "__main__":
    test_chat()
