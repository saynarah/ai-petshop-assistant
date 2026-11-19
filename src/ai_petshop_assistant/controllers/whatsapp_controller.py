
import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from ai_petshop_assistant.integrations.whatsapp_adapter import (
    extract_messages,
)
from ai_petshop_assistant.services.message_service import MessageService


load_dotenv()

router = APIRouter(
    prefix="/webhooks/whatsapp",
    tags=["WhatsApp"]
)

message_service = MessageService()


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    mode: str | None = Query(None, alias="hub.mode"),
    token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    expected_token = os.getenv("META_VERIFY_TOKEN")

    if (
        expected_token
        and mode == "subscribe"
        and token is not None
        and hmac.compare_digest(token, expected_token)
        and challenge is not None
    ):
        return challenge

    raise HTTPException(
        status_code=403,
        detail="Webhook verification failed"
    )


@router.post("")
async def receive_webhook(request: Request):
    app_secret = os.getenv("META_APP_SECRET")

    if not app_secret:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret not configured"
        )

    raw_body = await request.body()
    received_signature = request.headers.get(
        "X-Hub-Signature-256", ""
    )

    expected_signature = "sha256=" + hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        received_signature,
        expected_signature
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook signature"
        )

    try:
        payload = await request.json()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON"
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="Invalid payload"
        )

    messages = extract_messages(payload)

    for message in messages:
        message_service.process_message(message)

    return {"status": "received"}
