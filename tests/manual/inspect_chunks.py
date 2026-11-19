
from ai_petshop_assistant.dependencies import get_agent


agent = get_agent()

collection = agent.vectorstore._collection

results = collection.get(
    include=["documents", "metadatas"]
)

documents = results["documents"] or []
metadatas = results["metadatas"] or []

print(f"Total chunks: {len(documents)}")

for i, (content, metadata) in enumerate(
    zip(documents, metadatas),
    start=1
):
    print(f"\n{'=' * 60}")
    print(f"CHUNK {i}")
    print(f"Source: {metadata.get('source')}")
    print(f"Length: {len(content)} characters")
    print(f"{'=' * 60}")
    print(content)
