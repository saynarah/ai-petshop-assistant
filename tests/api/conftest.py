
import pytest

from unittest.mock import Mock
from fastapi.testclient import TestClient

from ai_petshop_assistant.main import app
from ai_petshop_assistant.dependencies import (
    get_document_ingestion_service,
    get_message_service,
)


@pytest.fixture
def mock_document_service():
    return Mock()


@pytest.fixture
def mock_message_service():
    return Mock()


@pytest.fixture
def client(
    mock_document_service,
    mock_message_service,
):
    app.dependency_overrides[
        get_document_ingestion_service
    ] = lambda: mock_document_service

    app.dependency_overrides[
        get_message_service
    ] = lambda: mock_message_service

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
