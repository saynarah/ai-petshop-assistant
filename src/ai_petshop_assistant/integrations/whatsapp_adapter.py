
from ai_petshop_assistant.schemas.message_schema import (
    MessageRequest,
)


def extract_messages(payload: dict) -> list[MessageRequest]:
    result = []

    if payload.get("object") != "whatsapp_business_account":
        return result

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue

            value = change.get("value", {})

            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue

                text = message.get("text", {}).get("body")

                if not isinstance(text, str) or not text.strip():
                    continue

                result.append(
                    MessageRequest(
                        message_id=message["id"],
                        customer_id=message["from"],
                        message=text,
                        channel="whatsapp",
                    )
                )

    return result
