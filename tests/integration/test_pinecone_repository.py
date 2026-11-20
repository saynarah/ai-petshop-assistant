
import os
import time
import uuid

import pytest

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from ai_petshop_assistant.repositories.pinecone_document_repository import (
    PineconeDocumentRepository,
)
from ai_petshop_assistant.services.document_ingestion_service import (
    DocumentIngestionService,
)


load_dotenv()

pytestmark = pytest.mark.external


def wait_for_records(
    repository,
    document_id,
    expected_hash,
    expected_count,
    timeout=60,
):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        records = repository.find_by_document_id(
            document_id
        )

        if (
            len(records) == expected_count
            and all(
                record["metadata"].get("content_hash")
                == expected_hash
                for record in records
            )
        ):
            return records

        time.sleep(2)

    pytest.fail(
        "Pinecone did not reach the expected state"
    )


@pytest.fixture
def pinecone_setup(monkeypatch):

    if os.getenv("RUN_PINECONE_TESTS") != "1":
        pytest.skip(
            "Set RUN_PINECONE_TESTS=1 to run external tests"
        )

    index_name = os.environ["PINECONE_INDEX_NAME"]
    namespace = f"test-{uuid.uuid4().hex[:12]}"

    monkeypatch.setenv(
        "PINECONE_NAMESPACE",
        namespace
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
    )

    repository = PineconeDocumentRepository(
        vectorstore=vectorstore
    )

    service = DocumentIngestionService(
        repository=repository,
        chunk_size=500,
        chunk_overlap=100,
    )

    yield service, repository

    # Clean up ONLY the isolated test namespace.
    client = Pinecone(
        api_key=os.environ["PINECONE_API_KEY"]
    )

    index = client.Index(index_name)

    index.delete(
        delete_all=True,
        namespace=namespace,
    )


def test_document_lifecycle_in_pinecone(pinecone_setup):

    service, repository = pinecone_setup

    filename = "integration_prices.md"

    # 1. New document
    first = service.ingest_text(
        filename,
        "O banho para cães pequenos custa R$ 50.",
    )

    assert first.status == "indexed"

    wait_for_records(
        repository,
        first.document_id,
        first.content_hash,
        first.chunks_created,
    )

    # 2. Unchanged document
    repeated = service.ingest_text(
        filename,
        "O banho para cães pequenos custa R$ 50.",
    )

    assert repeated.status == "unchanged"
    assert repeated.chunks_created == 0

    # 3. Update existing document
    updated = service.ingest_text(
        filename,
        "O banho para cães pequenos custa R$ 60.",
    )

    assert updated.status == "updated"

    wait_for_records(
        repository,
        updated.document_id,
        updated.content_hash,
        updated.chunks_created,
    )

    # 4. Same content, different filename
    duplicate = service.ingest_text(
        "another_prices.md",
        "O banho para cães pequenos custa R$ 60.",
    )

    assert duplicate.status == "duplicate"
    assert duplicate.chunks_created == 0
