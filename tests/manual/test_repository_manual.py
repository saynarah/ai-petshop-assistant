
from ai_petshop_assistant.dependencies import (
    get_document_repository,
    get_document_ingestion_service,
)


repository = get_document_repository()
service = get_document_ingestion_service()

filename = "teste_repository.md"

original_content = """
# Política de Atendimento

O pet shop funciona de segunda a sábado.
O serviço de banho precisa ser agendado.
"""

updated_content = """
# Política de Atendimento

O pet shop funciona de segunda a sábado.
O serviço de banho precisa ser agendado.
O cliente pode solicitar remarcação pelo atendimento.
"""


def show_result(label, result):
    print(f"\n{label}")
    print(result.model_dump())


first = service.ingest_text(filename, original_content)
show_result("FIRST UPLOAD", first)

second = service.ingest_text(filename, original_content)
show_result("REPEATED UPLOAD", second)

third = service.ingest_text(filename, updated_content)
show_result("UPDATED UPLOAD", third)

records = repository.find_by_document_id(
    third.document_id
)

print("\nFINAL CHUNKS")
for record in records:
    print(record["id"])
    print(record["metadata"]["content_hash"])

assert first.status in ("indexed", "updated", "unchanged")
assert second.status == "unchanged"
assert third.status == "updated"
assert len(records) == third.chunks_created

assert all(
    record["metadata"]["content_hash"] == third.content_hash
    for record in records
)

print("\nRepository tests passed!")
