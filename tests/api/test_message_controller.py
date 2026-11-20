
from ai_petshop_assistant.schemas.message_schema import (
    ChatResponseStructured,
)


ENDPOINT = "/messages/chat"


def test_chat_returns_structured_response(
    client,
    mock_message_service,
):

    mock_message_service.generate_reply.return_value = (
        ChatResponseStructured(
            message_id="msg123",
            customer_id="customer123",
            reply="O banho para cães pequenos custa R$ 50.",
            confidence="high",
            sources=["politica_precos.md"],
            needs_human_review=False,
        )
    )

    payload = {
        "message_id": "msg123",
        "customer_id": "customer123",
        "message": "Quanto custa o banho?",
        "channel": "whatsapp",
    }

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["message_id"] == "msg123"
    assert body["customer_id"] == "customer123"
    assert body["confidence"] == "high"
    assert body["needs_human_review"] is False
    assert "politica_precos.md" in body["sources"]

    mock_message_service.generate_reply.assert_called_once()


def test_chat_rejects_missing_required_fields(
    client,
    mock_message_service,
):

    response = client.post(
        ENDPOINT,
        json={
            "message": "Quanto custa o banho?"
        },
    )

    assert response.status_code == 422
    mock_message_service.generate_reply.assert_not_called()
