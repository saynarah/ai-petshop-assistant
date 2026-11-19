from pydantic import BaseModel, Field, model_validator
from typing import List, Literal


class MessageRequest(BaseModel):
    message_id: str
    customer_id: str
    message: str = Field(min_length=1)
    channel: str = "whatsapp"


class MessageResponse(BaseModel):
    message_id: str
    status: str
    detail: str


class ChatResponse(BaseModel):
    message_id: str
    customer_id: str
    reply: str
    status: str

class AgentResponse(BaseModel):
    reply: str
    confidence: Literal["high", "medium", "low"]
    sources: list[str] = Field(default_factory=list)
    needs_human_review: bool

    @model_validator(mode="after")
    def validate_review(self):
        self.needs_human_review = (
            self.confidence in (
                "medium", 
                "low")
        )
        return self

class ChatResponseStructured(AgentResponse):
    message_id: str
    customer_id: str



