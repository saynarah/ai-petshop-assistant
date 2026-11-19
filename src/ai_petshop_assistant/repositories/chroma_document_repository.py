
from langchain_chroma import Chroma
from langchain_core.documents import Document

from ai_petshop_assistant.repositories.vector_document_repository import (
    VectorDocumentRepository,
)


class ChromaDocumentRepository(VectorDocumentRepository):

    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore

    def _find_by_metadata(
        self,
        field: str,
        value: str,
    ) -> list[dict]:

        results = self.vectorstore.get(
            where={field: value},
            include=["metadatas"],
        )

        records = []

        for chunk_id, metadata in zip(
            results["ids"],
            results["metadatas"] or [],
        ):
            records.append({
                "id": chunk_id,
                "metadata": metadata or {},
            })

        return records

    def find_by_document_id(
        self,
        document_id: str,
    ) -> list[dict]:

        return self._find_by_metadata(
            "document_id",
            document_id,
        )

    def find_by_content_hash(
        self,
        content_hash: str,
    ) -> list[dict]:

        return self._find_by_metadata(
            "content_hash",
            content_hash,
        )

    def add_chunks(
        self,
        chunks: list[Document],
        ids: list[str],
    ) -> None:

        if not chunks:
            return

        self.vectorstore.add_documents(
            documents=chunks,
            ids=ids,
        )

    def delete_chunks(
        self,
        ids: list[str],
    ) -> None:

        if ids:
            self.vectorstore.delete(ids=ids)
