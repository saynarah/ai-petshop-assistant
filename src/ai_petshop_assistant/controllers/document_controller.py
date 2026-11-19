
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ai_petshop_assistant.agents.petshop_agent import PetShopAgent
from ai_petshop_assistant.dependencies import get_agent, get_document_ingestion_service
from ai_petshop_assistant.schemas.document_schema import (
    DocumentUploadResponse,
)
from ai_petshop_assistant.services.document_ingestion_service import (
    DocumentIngestionService,
)


router = APIRouter(
    prefix="/admin/documents",
    tags=["Documents"],
)

ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_FILE_SIZE = 1024 * 1024  # 1 MB


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
def upload_document(
    file: UploadFile = File(...),
    service: DocumentIngestionService = Depends(
    get_document_ingestion_service
)
):

    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported",
        )

    try:
        content_bytes = file.file.read(MAX_FILE_SIZE + 1)
    finally:
        file.file.close()

    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large",
        )

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must use UTF-8 encoding",
        )

    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="File is empty",
        )

    return service.ingest_text(
        filename=filename,
        content=content,
    )
