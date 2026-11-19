
from ai_petshop_assistant.dependencies import get_agent

agent = get_agent()

question = "Quanto custa o banho de um Golden Retriever?"

retriever = agent._build_retriever(
    use_advanced=False
)

docs = retriever.invoke(question)

for i, doc in enumerate(docs, start=1):
    print(f"\n--- Result {i} ---")
    print("Source:", doc.metadata.get("source"))
    print("Content:", doc.page_content)
