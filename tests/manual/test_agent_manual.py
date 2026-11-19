
from langchain_core.documents import Document

from ai_petshop_assistant.agents.petshop_agent import PetShopAgent
from ai_petshop_assistant.dependencies import get_agent


def main():

    agent = PetShopAgent(
        persist_directory="./data/chroma"
    )

    documents = [
        Document(
            page_content=(
                "O pet shop oferece banho para cães de pequeno, "
                "médio e grande porte. "
                "O banho de cães de pequeno porte custa R$ 50."
            ),
            metadata={"source": "tabela_precos"}
        ),
        Document(
            page_content=(
                "O serviço de tosa higiênica custa R$ 35. "
                "A tosa completa deve ser orçada individualmente."
            ),
            metadata={"source": "servicos"}
        ),
        Document(
            page_content=(
                "O pet shop funciona de segunda a sábado, "
                "das 8h às 18h. "
                "Os agendamentos precisam ser confirmados "
                "pela equipe."
            ),
            metadata={"source": "horarios"}
        ),
    ]

    count = agent.add_documents(documents)

    print(f"Total de chunks adicionados: {count}")

    retriever = agent._build_retriever(use_advanced=False)

    docs = retriever.invoke(
        "Quanto custa o banho para um cachorro pequeno?"
    )

    for index, doc in enumerate(docs):
        print(f"\nDocument {index + 1}")
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}")


    response = agent.ask("123",
                         "Quanto custa o banho para um cachorro pequeno?",                          
                         use_advanced=False,
                         )
    print(f"\nResponse: {response}")

    response = agent.ask("123",
                         "Quanto custa uma consulta veterinária?", 
                         use_advanced=False)
    
    print(f"\nResponse 02: {response}")


if __name__ == "__main__":
    main()
