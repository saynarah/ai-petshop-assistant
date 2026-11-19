from typing import Literal
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: Literal[
        "indexed",
        "unchanged",
        "updated",
        "duplicate"
    ]
    content_hash: str
    chunks_created: int
    source: str
