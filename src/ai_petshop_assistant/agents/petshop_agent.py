from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from typing import List, Optional, Dict
from langchain_core.documents import Document
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from ai_petshop_assistant.schemas.message_schema import ChatResponseStructured, AgentResponse
from ai_petshop_assistant.prompts import (
    PETSHOP_SYSTEM_PROMPT,
    QUERY_REWRITING_PROMPT
    )
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.vectorstores import VectorStore

load_dotenv()

class PetShopAgent:

    def __init__( 
            self,  
            vectorstore: VectorStore,
            chunk_size: int = 500,
            chunk_overlap: int = 100
    ):
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        self.customer_store: Dict[str, InMemoryChatMessageHistory] = {}

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        self.vectorstore = vectorstore

        print(f"PetShop agent initialized")
 

    def add_documents(
              self,
              documents: List[Document],
              source_name: Optional[str] = None,
        ) -> int:
            
        if source_name:
            for doc in documents:
                doc.metadata["source"] = source_name

        chunks = self.splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata["indexed_at"] = datetime.now().isoformat()

        self.vectorstore.add_documents(chunks)
        print(f"Added {len(chunks)} chunks from {len(documents)} documents")

        return len(chunks)
    
    def _build_retriever(self, 
                         use_advanced: bool = False,
                         k: int = 3):

        base_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        if not use_advanced:
            return base_retriever

        multi_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=self.llm,
            include_original=True
        )

        multi_retriever.verbose = True

        return multi_retriever

    def _build_history_aware_retriever(
            self,
            use_advanced: bool = False,
            k: int = 3):

        base_retriever = self._build_retriever(
            use_advanced=use_advanced,
            k=k
        )

        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm,
            retriever=base_retriever,
            prompt=QUERY_REWRITING_PROMPT,
        )

        return history_aware_retriever

    def _format_docs_for_context(self, docs) -> str:
        if not docs:
            return "No relevant documents found."

        formatted = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown source")
            formatted.append(f"--- Chunk {i+1} [Source: {source}] ---\n{doc.page_content}")
        return "\n\n".join(formatted)

    def list_sources(self) -> List[str]:
        results = self.vectorstore._collection.get()
        sources = set()
        for metadata in results.get("metadatas", []):
            if metadata and "source" in metadata:
                sources.add(metadata["source"])
        return sorted(list(sources))
    
    def ask(self, customer_id: str, question: str, message_id: str = None, use_advanced: bool = False) -> ChatResponseStructured:
        #Ask a question against the indexed documents

        history_aware_retriever = self._build_history_aware_retriever(
            use_advanced=use_advanced
        ).with_config({"run_name": "PetShop History-Aware Retrieval"})

        history = self._get_customer_history(customer_id)

             
        # retriever = self._build_retriever(use_advanced=use_advanced)
        docs = history_aware_retriever.invoke(
            {
                "input": question,
                "chat_history": history.messages[-10:]
            }
        )

        context = self._format_docs_for_context(docs)
        sources = list(dict.fromkeys(
                doc.metadata["source"]
                for doc in docs
                if doc.metadata.get("source")
        ))

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PETSHOP_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human",
                """
                Context documents: 
                {context}

                Available sources: {sources}

                Question: {question}

                Provide a clear answer with source citations.
                """),
            ]
        )
        
        llm_structured = self.llm.with_structured_output(AgentResponse)
        

        chain = prompt | llm_structured

        agent_response = chain.invoke(
            {
                "context": context,
                "question": question,
                "sources": ", ".join(sources),
                "history": history.messages[-10:],
            }
        )

        history.add_message(HumanMessage(content=question))
        history.add_message(AIMessage(content=agent_response.reply))

        return ChatResponseStructured(
            message_id=message_id,
            customer_id=customer_id,
            **agent_response.model_dump()
        )

    def _get_customer_history(self, customer_id: str) -> BaseChatMessageHistory:
        if customer_id not in self.customer_store:
            self.customer_store[customer_id] = InMemoryChatMessageHistory()
        return self.customer_store[customer_id]

    def index_document(
            self,
            document: Document,
            document_id: str,
            content_hash: str,
    ) -> int:

        chunks = self.splitter.split_documents([document])

        timestamp = datetime.now().isoformat()

        chunk_ids = []

        for index, chunk in enumerate(chunks):

            chunk.metadata.update({
                "document_id": document_id,
                "content_hash": content_hash,
                "chunk_index": index,
                "indexed_at": timestamp,
            })

            chunk_id = (
                f"{document_id}:"
                f"{content_hash}:"
                f"{index}"
            )

            chunk_ids.append(chunk_id)

        if chunks:
            self.vectorstore.add_documents(
                documents=chunks,
                ids=chunk_ids
            )

        return len(chunks)
        