
from ai_petshop_assistant.dependencies import (
    get_document_ingestion_service,
    get_document_repository,
)


repository = get_document_repository()
service = get_document_ingestion_service()

print("Repository:", type(repository).__name__)

filename = "pinecone_repository_test.md"

content = """
# Política de Banho e Tosa

O Pet Shop Amigo Animal oferece banho para cães pequenos
por R$ 50.

A tosa higiênica para cães pequenos custa R$ 35.

Os serviços podem ser realizados no mesmo atendimento.
"""

# First upload
result = service.ingest_text(
    filename=filename,
    content=content,
)

print("\nFirst upload:")
print(result.model_dump())

# Search by document ID
records = repository.find_by_document_id(
    result.document_id
)

print("\nChunks found:", len(records))

for record in records:
    print(record["id"])
    print(record["metadata"])

# Search by content hash
matching = repository.find_by_content_hash(
    result.content_hash
)

print("\nChunks with matching hash:", len(matching))
