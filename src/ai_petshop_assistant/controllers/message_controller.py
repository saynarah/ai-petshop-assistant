from fastapi import APIRouter, Depends
from typing import Annotated
from ai_petshop_assistant.schemas.message_schema import (
    MessageRequest, 
    MessageResponse,
    ChatResponse,
    ChatResponseStructured
)

from ai_petshop_assistant.services.message_service import MessageService
from ai_petshop_assistant.dependencies import get_message_service
from ai_petshop_assistant.schemas.message_schema import MessageRequest, ChatResponse

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.post(
    "/chat",
    response_model=ChatResponseStructured
)
def chat(request: MessageRequest,
         service: Annotated[
            MessageService,
            Depends(get_message_service)]
         ) -> ChatResponseStructured:

    return service.generate_reply(request)

