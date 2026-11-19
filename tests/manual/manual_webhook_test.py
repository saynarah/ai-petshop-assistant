
import hashlib
import hmac
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)

payload = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "changes": [
                {
                    "field": "messages",
                    "value": {
                        "messages": [
                            {
                                "id": "wamid.test001",
                                "from": "5500000000000",
                                "type": "text",
                                "text": {
                                    "body": "Quanto custa o banho?"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

body = json.dumps(payload).encode("utf-8")

secret = os.environ["META_APP_SECRET"]

signature = "sha256=" + hmac.new(
    secret.encode("utf-8"),
    body,
    hashlib.sha256
).hexdigest()

response = httpx.post(
    "http://127.0.0.1:8000/webhooks/whatsapp",
    content=body,
    headers={
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature
    },
    timeout=10.0
)

print(response.status_code)
print(response.json())
