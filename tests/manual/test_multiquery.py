
from langchain_core.messages import HumanMessage, AIMessage

from ai_petshop_assistant.dependencies import get_agent


agent = get_agent()

history = [
    HumanMessage(
        content="Tenho um Shih Tzu chamado Thor."
    ),
    AIMessage(
        content="Olá! Como posso ajudar com o Thor?"
    ),
]

question = "Quanto custa o banho dele com tosa higiênica?"

for advanced in [False, True]:

    print(f"\n{'=' * 60}")
    print(f"MULTIQUERY ENABLED: {advanced}")
    print(f"{'=' * 60}")

    retriever = agent._build_history_aware_retriever(
        use_advanced=advanced
    )

    docs = retriever.invoke({
        "input": question,
        "chat_history": history,
    })

    print(f"\nDocuments retrieved: {len(docs)}")

    for i, doc in enumerate(docs, start=1):
        print(f"\n--- Chunk {i} ---")
        print("Source:", doc.metadata.get("source"))
        print("Content:", doc.page_content[:350])
