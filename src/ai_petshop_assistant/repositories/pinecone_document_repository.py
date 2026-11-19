
import os

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from ai_petshop_assistant.repositories.vector_document_repository import (
    VectorDocumentRepository,
)


load_dotenv()


class PineconeDocumentRepository(VectorDocumentRepository):

    def __init__(
        self,
        vectorstore: PineconeVectorStore,
    ):
        self.vectorstore = vectorstore

        self.namespace = os.getenv(
            "PINECONE_NAMESPACE",
            "petshop-dev"
        )

        index_name = os.environ["PINECONE_INDEX_NAME"]

        self.client = Pinecone(
            api_key=os.environ["PINECONE_API_KEY"]
        )

        self.index = self.client.Index(index_name)

    def add_chunks(
        self,
        chunks: list[Document],
        ids: list[str],
    ) -> None:

        if not chunks:
            return

        if len(chunks) != len(ids):
            raise ValueError(
                "Chunks and IDs must have the same length"
            )

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


    def _fetch_records(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []

        response = self.index.fetch(
            ids=ids,
            namespace=self.namespace,
        )

        return [
            {
                "id": vector_id,
                "metadata": dict(vector.metadata or {}),
            }
            for vector_id, vector in response.vectors.items()
        ]


    def find_by_document_id(
        self,
        document_id: str,
    ) -> list[dict]:

        records = []
        prefix = f"{document_id}:"

        for ids_batch in self.index.list(
            prefix=prefix,
            namespace=self.namespace,
        ):
            records.extend(
                self._fetch_records(ids_batch)
            )

        return records


    def find_by_content_hash(
        self,
        content_hash: str,
    ) -> list[dict]:

        records = []

        # Scan all IDs in the namespace.
        for ids_batch in self.index.list(
            namespace=self.namespace,
        ):
            batch_records = self._fetch_records(
                ids_batch
            )

            for record in batch_records:
                if (
                    record["metadata"].get("content_hash")
                    == content_hash
                ):
                    records.append(record)

        return records
