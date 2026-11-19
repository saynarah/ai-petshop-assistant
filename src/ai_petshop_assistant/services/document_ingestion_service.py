
import hashlib
from datetime import datetime, timezone

from langchain_core.documents import Document

from ai_petshop_assistant.schemas.document_schema import (
    DocumentUploadResponse,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from ai_petshop_assistant.repositories.chroma_document_repository import VectorDocumentRepository


class DocumentIngestionService:

    def __init__(
            self, 
            repository: VectorDocumentRepository,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
        ):
        self.repository = repository

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def ingest_text(
        self,
        filename: str,
        content: str,
    ) -> DocumentUploadResponse:

        # 1. Generate document identifiers
        normalized_filename = filename.strip()

        document_id = hashlib.sha256(
            normalized_filename.encode("utf-8")
        ).hexdigest()

        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        
        # 2. Find previous versions of this document
        existing = self.repository.find_by_document_id(document_id)

        existing_ids = [item["id"] for item in existing]

        existing_hashes  = {
            item["metadata"].get("content_hash")
            for item in existing
        }

        # 3. Unchanged document
        if existing and existing_hashes == {content_hash}:
            return DocumentUploadResponse(
                document_id=document_id,
                filename=filename,
                status="unchanged",
                content_hash=content_hash,
                chunks_created=0,
                source=filename,
            )

        # 4. Same content under another filename
        matching = self.repository.find_by_content_hash(
            content_hash
        )

        for item in matching:
            metadata = item["metadata"]

            if metadata.get("document_id") != document_id:
                return DocumentUploadResponse(
                    document_id=metadata["document_id"],
                    filename=filename,
                    status="duplicate",
                    content_hash=content_hash,
                    chunks_created=0,
                    source=metadata.get("source", filename),
                )

        # 5. Create and split document
        document = Document(
            page_content=content,
            metadata={
                "source": filename,
                "document_id": document_id,
                "content_hash": content_hash,
                "file_type": filename.rsplit(".", 1)[-1].lower(),
            },
        )

        chunks = self.splitter.split_documents([document])

        # 6. Add metadata and stable chunk IDs
        timestamp = datetime.now(timezone.utc).isoformat()
        chunk_ids = []

        for index, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index": index,
                "indexed_at": timestamp,
            })

            chunk_ids.append(
                f"{document_id}:{content_hash}:{index}"
            )

        # 7. Write new version
        self.repository.add_chunks(
            chunks=chunks,
            ids=chunk_ids,
        )

        # 8. Remove previous version
        if existing_ids:
            self.repository.delete_chunks(existing_ids)
            status = "updated"
        else:
            status = "indexed"

        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            status=status,
            content_hash=content_hash,
            chunks_created=len(chunks),
            source=filename,
        )

        