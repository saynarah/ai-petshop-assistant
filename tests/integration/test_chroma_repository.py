
import hashlib

import pytest

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from ai_petshop_assistant.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)
from ai_petshop_assistant.services.document_ingestion_service import (
    DocumentIngestionService,
)


class TestEmbeddings(Embeddings):
    """Embeddings determinísticos, apenas para testes."""

    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest]

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


@pytest.fixture
def chroma_store(tmp_path):
    return Chroma(
        collection_name="integration_tests",
        persist_directory=str(tmp_path / "chroma"),
        embedding_function=TestEmbeddings(),
    )


@pytest.fixture
def repository(chroma_store):
    return ChromaDocumentRepository(
        vectorstore=chroma_store
    )


@pytest.fixture
def service(repository):
    return DocumentIngestionService(
        repository=repository,
        chunk_size=100,
        chunk_overlap=20,
    )


def test_index_and_find_document(service, repository):

    result = service.ingest_text(
        "servicos.md",
        (
            "O banho para cães pequenos custa R$ 50. "
            "A tosa higiênica custa R$ 35."
        ),
    )

    records = repository.find_by_document_id(
        result.document_id
    )

    assert result.status == "indexed"
    assert len(records) == result.chunks_created

    assert all(
        record["metadata"]["document_id"] == result.document_id
        for record in records
    )


def test_duplicate_upload_does_not_create_chunks(
    service,
    repository,
):

    content = "O pet shop funciona de segunda a sábado."

    first = service.ingest_text("horarios.md", content)
    second = service.ingest_text("horarios.md", content)

    records = repository.find_by_document_id(
        first.document_id
    )

    assert second.status == "unchanged"
    assert second.chunks_created == 0
    assert len(records) == first.chunks_created


def test_update_removes_old_chunks(service, repository):

    first = service.ingest_text(
        "precos.md",
        "O banho custa R$ 50.",
    )

    old_records = repository.find_by_document_id(
        first.document_id
    )

    old_ids = {record["id"] for record in old_records}

    updated = service.ingest_text(
        "precos.md",
        "O banho custa R$ 60.",
    )

    new_records = repository.find_by_document_id(
        updated.document_id
    )

    new_ids = {record["id"] for record in new_records}

    assert updated.status == "updated"
    assert updated.content_hash != first.content_hash
    assert old_ids.isdisjoint(new_ids)

    assert all(
        record["metadata"]["content_hash"]
        == updated.content_hash
        for record in new_records
    )


def test_identical_content_with_different_filename(
    service,
    repository,
):

    content = "A loja aceita pagamentos via Pix."

    first = service.ingest_text(
        "pagamentos.md", content
    )

    second = service.ingest_text(
        "copia_pagamentos.md", content
    )

    assert first.status == "indexed"
    assert second.status == "duplicate"
    assert second.chunks_created == 0
    assert second.document_id == first.document_id


def test_similarity_search_returns_indexed_content(
    service,
    chroma_store,
):

    service.ingest_text(
        "politica.md",
        "O pet shop aceita pagamentos via Pix.",
    )

    results = chroma_store.similarity_search(
        "Quais formas de pagamento são aceitas?",
        k=3,
    )

    assert results
    assert any(
        "Pix" in document.page_content
        for document in results
    )
