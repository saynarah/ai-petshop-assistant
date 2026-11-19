from functools import lru_cache
import os
from ai_petshop_assistant.agents.petshop_agent import PetShopAgent
from ai_petshop_assistant.services.message_service import MessageService
from ai_petshop_assistant.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)
from ai_petshop_assistant.repositories.vector_document_repository import (
    VectorDocumentRepository,
)
from ai_petshop_assistant.repositories.pinecone_document_repository import (
    PineconeDocumentRepository,
)

from ai_petshop_assistant.services.document_ingestion_service import (
    DocumentIngestionService,
)
from langchain_openai import OpenAIEmbeddings
from ai_petshop_assistant.providers.vector_store_provider import (
    VectorStoreProvider,
)
from langchain_core.vectorstores import VectorStore
from dotenv import load_dotenv

load_dotenv()

@lru_cache
def get_vectorstore() -> VectorStore:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    return VectorStoreProvider.create(
        embeddings=embeddings
    )

@lru_cache
def get_agent() -> PetShopAgent:

    return PetShopAgent(
        vectorstore=get_vectorstore()
    )


def get_message_service() -> MessageService:
    return MessageService(
        agent=get_agent())


def get_document_repository() -> VectorDocumentRepository:

    provider = os.getenv(
        "VECTOR_STORE_PROVIDER", "chroma"
    ).lower()

    vectorstore = get_vectorstore()

    if provider == "chroma":
        return ChromaDocumentRepository(
            vectorstore=vectorstore
        )
    if provider == "pinecone":
        return PineconeDocumentRepository(
            vectorstore=vectorstore
        )
    raise ValueError(f"Unsupported vector store provider: {provider}")
    


def get_document_ingestion_service() -> DocumentIngestionService:
    return DocumentIngestionService(
        repository=get_document_repository()
    )









@lru_cache
def get_agent() -> PetShopAgent:
    return PetShopAgent(
        vectorstore=get_vectorstore()
    )




