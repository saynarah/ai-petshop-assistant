
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore


load_dotenv()


class VectorStoreProvider:

    @staticmethod
    def create(embeddings: Embeddings) -> VectorStore:

        provider = os.getenv(
            "VECTOR_STORE_PROVIDER", "chroma"
        ).lower()

        if provider == "chroma":

            project_root = (
                Path(__file__).resolve().parents[3]
            )

            chroma_dir = project_root / "data" / "chroma"

            return Chroma(
                persist_directory=str(chroma_dir),
                embedding_function=embeddings,
                collection_name="petshop_docs",
            )

        if provider == "pinecone":

            index_name = os.environ[
                "PINECONE_INDEX_NAME"
            ]

            namespace = os.getenv(
                "PINECONE_NAMESPACE", "petshop-dev"
            )

            return PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings,
                namespace=namespace,
            )

        raise ValueError(
            f"Unsupported vector store provider: {provider}"
        )
