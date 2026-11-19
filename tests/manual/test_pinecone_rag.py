
from langchain_core.documents import Document

from ai_petshop_assistant.dependencies import (
    get_vectorstore,
)


vectorstore = get_vectorstore()

documents = [
    Document(
        page_content=(
            "O Pet Shop Amigo Animal oferece banho "
            "para cães de pequeno porte por R$ 50."
        ),
        metadata={
            "source": "pinecone_smoke_test",
            "category": "pricing",
        },
    ),
    Document(
        page_content=(
            "A tosa higiênica para cães pequenos "
            "custa R$ 35."
        ),
        metadata={
            "source": "pinecone_smoke_test",
            "category": "services",
        },
    ),
]

vectorstore.add_documents(
    documents=documents,
    ids=[
        "smoke-test-banho",
        "smoke-test-tosa",
    ],
)

print("Documents indexed.")

results = vectorstore.similarity_search(
    "Quanto custa o banho para um cachorro pequeno?",
    k=2,
)

for doc in results:
    print("\nSource:", doc.metadata.get("source"))
    print("Content:", doc.page_content)
