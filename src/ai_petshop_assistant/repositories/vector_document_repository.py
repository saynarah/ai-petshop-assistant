
from abc import ABC, abstractmethod

from langchain_core.documents import Document


class VectorDocumentRepository(ABC):

    @abstractmethod
    def find_by_document_id(
        self,
        document_id: str,
    ) -> list[dict]:
        pass

    @abstractmethod
    def find_by_content_hash(
        self,
        content_hash: str,
    ) -> list[dict]:
        pass

    @abstractmethod
    def add_chunks(
        self,
        chunks: list[Document],
        ids: list[str],
    ) -> None:
        pass

    @abstractmethod
    def delete_chunks(
        self,
        ids: list[str],
    ) -> None:
        pass
