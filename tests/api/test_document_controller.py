
from ai_petshop_assistant.schemas.document_schema import (
    DocumentUploadResponse,
)


ENDPOINT = "/admin/documents/upload"


def test_upload_valid_document(client, mock_document_service):

    mock_document_service.ingest_text.return_value = (
        DocumentUploadResponse(
            document_id="doc123",
            filename="politica.md",
            status="indexed",
            content_hash="hash123",
            chunks_created=3,
            source="politica.md",
        )
    )

    response = client.post(
        ENDPOINT,
        files={
            "file": (
                "politica.md",
                b"# Politica de atendimento\nAtendimento aos sabados.",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "indexed"
    assert body["chunks_created"] == 3
    assert body["document_id"] == "doc123"

    mock_document_service.ingest_text.assert_called_once_with(
        filename="politica.md",
        content="# Politica de atendimento\nAtendimento aos sabados.",
    )


def test_reject_unsupported_extension(
    client,
    mock_document_service,
):

    response = client.post(
        ENDPOINT,
        files={
            "file": (
                "arquivo.exe",
                b"invalid file",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    mock_document_service.ingest_text.assert_not_called()


def test_reject_empty_file(client, mock_document_service):

    response = client.post(
        ENDPOINT,
        files={
            "file": (
                "empty.md",
                b"",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 400
    mock_document_service.ingest_text.assert_not_called()


def test_reject_file_above_size_limit(
    client,
    mock_document_service,
):

    oversized_content = b"a" * (1024 * 1024 + 1)

    response = client.post(
        ENDPOINT,
        files={
            "file": (
                "large.md",
                oversized_content,
                "text/markdown",
            )
        },
    )

    assert response.status_code == 413
    mock_document_service.ingest_text.assert_not_called()


def test_reject_invalid_utf8(
    client,
    mock_document_service,
):

    response = client.post(
        ENDPOINT,
        files={
            "file": (
                "invalid.md",
                b"\xff\xfe",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 400
    mock_document_service.ingest_text.assert_not_called()


def test_reject_missing_file(client, mock_document_service):

    response = client.post(ENDPOINT)

    assert response.status_code == 422
    mock_document_service.ingest_text.assert_not_called()



def test_upload_propagates_internal_error(
    mock_document_service,
):
    from fastapi.testclient import TestClient
    from ai_petshop_assistant.main import app
    from ai_petshop_assistant.dependencies import (
        get_document_ingestion_service,
    )

    mock_document_service.ingest_text.side_effect = (
        RuntimeError("Vector store unavailable")
    )

    app.dependency_overrides[
        get_document_ingestion_service
    ] = lambda: mock_document_service

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as client:

            response = client.post(
                ENDPOINT,
                files={
                    "file": (
                        "test.md",
                        b"Valid content",
                        "text/markdown",
                    )
                },
            )

            assert response.status_code == 500

    finally:
        app.dependency_overrides.clear()

