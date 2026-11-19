import logging

from ai_petshop_assistant.agents.petshop_agent import PetShopAgent
from ai_petshop_assistant.schemas.message_schema import (
    MessageRequest,
    MessageResponse,
    ChatResponse,
    ChatResponseStructured
)

logger = logging.getLogger(__name__)

class MessageService:

    def __init__(self, agent=PetShopAgent):
        self.agent = agent

    def generate_reply(
            self,
            request: MessageRequest
    ) -> ChatResponseStructured:

        logger.info(
            "Generating reply for message_id=%s",
            request.message_id
        )

        try: 
            response = self.agent.ask(
                customer_id=request.customer_id,
                question=request.message,
                message_id=request.message_id,
                use_advanced=False
            )

        except Exception:
            logger.exception(
                "Error generating reply for message_id=%s",
                request.message_id
            )

            return ChatResponseStructured(
                message_id=request.message_id,
                customer_id=request.customer_id,
                reply="I could not generate a reply. Our team will get back to you shortly.",
                confidence="low",
                sources=[],
                needs_human_review=True
            )
        
        return ChatResponseStructured(
            message_id=request.message_id,
            customer_id=request.customer_id,
            reply=response.reply,
            confidence=response.confidence,
            sources=response.sources,
            needs_human_review=response.needs_human_review
        )