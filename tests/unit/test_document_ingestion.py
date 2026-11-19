
import pytest

from langchain_core.documents import Document

from ai_petshop_assistant.repositories.vector_document_repository import (
    VectorDocumentRepository,
)
from ai_petshop_assistant.services.document_ingestion_service import (
    DocumentIngestionService,
)


class FakeVectorDocumentRepository(VectorDocumentRepository):

    def __init__(self):
        self.records = {}

    def find_by_document_id(self, document_id: str) -> list[dict]:
        return [
            record
            for record in self.records.values()
            if record["metadata"].get("document_id") == document_id
        ]

    def find_by_content_hash(self, content_hash: str) -> list[dict]:
        return [
            record
            for record in self.records.values()
            if record["metadata"].get("content_hash") == content_hash
        ]

    def add_chunks(
        self,
        chunks: list[Document],
        ids: list[str],
    ) -> None:

        for chunk_id, chunk in zip(ids, chunks, strict=True):
            self.records[chunk_id] = {
                "id": chunk_id,
                "metadata": dict(chunk.metadata),
                "content": chunk.page_content,
            }

    def delete_chunks(self, ids: list[str]) -> None:
        for chunk_id in ids:
            self.records.pop(chunk_id, None)



@pytest.fixture
def repository():
    return FakeVectorDocumentRepository()


@pytest.fixture
def service(repository):
    return DocumentIngestionService(
        repository=repository,
        chunk_size=100,
        chunk_overlap=20,
    )



def test_should_index_new_document(service, repository):

    result = service.ingest_text(
        filename="precos.md",
        content="Banho para cães pequenos custa R$ 50."
    )

    assert result.status == "indexed"
    assert result.chunks_created > 0
    assert result.document_id

    records = repository.find_by_document_id(
        result.document_id
    )

    assert len(records) == result.chunks_created


def test_should_not_index_unchanged_document(service, repository):

    filename = "precos.md"
    content = "Banho para cães pequenos custa R$ 50."

    first = service.ingest_text(filename, content)
    count_before = len(repository.records)

    second = service.ingest_text(filename, content)

    assert first.status == "indexed"
    assert second.status == "unchanged"
    assert second.chunks_created == 0
    assert len(repository.records) == count_before


def test_should_update_existing_document(service, repository):

    filename = "precos.md"

    first = service.ingest_text(
        filename,
        "Banho para cães pequenos custa R$ 50."
    )

    old_ids = {
        record["id"]
        for record in repository.find_by_document_id(
            first.document_id
        )
    }

    updated = service.ingest_text(
        filename,
        "Banho para cães pequenos custa R$ 60."
    )

    records = repository.find_by_document_id(
        updated.document_id
    )

    new_ids = {record["id"] for record in records}

    assert updated.status == "updated"
    assert updated.document_id == first.document_id
    assert updated.content_hash != first.content_hash

    assert not (old_ids & new_ids)

    assert all(
        record["metadata"]["content_hash"] == updated.content_hash
        for record in records
    )

    assert all(
        "R$ 60" in record["content"]
        for record in records
    )


def test_should_detect_same_content_with_different_name(
    service,
    repository
):

    content = "O pet shop atende aos sábados."

    first = service.ingest_text(
        "horarios.md",
        content
    )

    second = service.ingest_text(
        "copia_horarios.md",
        content
    )

    assert first.status == "indexed"
    assert second.status == "duplicate"
    assert second.chunks_created == 0
    assert second.document_id == first.document_id

    assert len(repository.records) == first.chunks_created


def test_should_preserve_document_metadata(service, repository):

    result = service.ingest_text(
        filename="servicos.md",
        content="O pet shop oferece banho e tosa."
    )

    records = repository.find_by_document_id(
        result.document_id
    )

    assert records

    for record in records:
        metadata = record["metadata"]

        assert metadata["source"] == "servicos.md"
        assert metadata["file_type"] == "md"
        assert metadata["document_id"] == result.document_id
        assert metadata["content_hash"] == result.content_hash
        assert isinstance(metadata["chunk_index"], int)

    
    