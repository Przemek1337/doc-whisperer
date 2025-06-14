from typing import Dict, List, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph.graph import CompiledGraph

from config.settings import settings
from core.vector_store import VectorStore
from core.document_processor import DocumentProcessor

class RAGState:
    def __init__(self):
        self.query: str = ""
        self.retrieved_documents: List = []
        self.context: str = ""
        self.response: str = ""
        self.metadata: Dict = {}

class RAGWorkflow:
    def __init__(self, collection_name: str = "documents"):
        self.vector_store = VectorStore(collection_name)
        self.document_processor = DocumentProcessor()
        self.llm = ChatOpenAI(
            model=settings.CHAT_MODEL,
            temperature=settings.TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self.workflow = self._create_workflow()
    def _create_workflow(self) -> CompiledGraph:
        workflow = StateGraph(dict)

        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate_context", self._generate_context)
        workflow.add_node("generate_response", self._generate_response)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate_context")
        workflow.add_edge("generate_context", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _retrieve_documents(self, state: Dict) -> Dict:
        query = state["query"]

        try:
            documents = self.vector_store.similarity_search(
                query=query,
                k=settings.TOP_K_DOCUMENTS
            )

            state["retrieved_documents"] = documents
            state["metadata"]["retrieved_documents"] = len(documents)

            return state
        except Exception as e:
            state["retrieved_documents"] = []
            state["metadata"]["retrieved_documents"] = f"Error retrieving documents: {e}"
            return state

    def _generate_context(self, state: Dict) -> Dict:
        documents = state["retrieved_documents"]

        if not documents:
            state["context"] = "No revelant documents"
            return state

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content.strip()
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        state["context"] = "\n\n".join(context_parts)
        return state

    def _generate_response(self, state: Dict) -> Dict:
        query = state["query"]
        context = state["context"]

        from utils.prompts import system_prompt

        try:
            messages = [
                SystemMessage(content=system_prompt.format(context=context)),
                HumanMessage(content=query)
            ]

            response = self.llm.invoke(messages)
            state["response"] = response.content

        except Exception as e:
            state["response"] = f"Error generating response: {e}"

        return state

    def process_query(self, query: str) -> Dict:
        initial_state = {
            "query": query,
            "retrieved_documents": [],
            "context": "",
            "response": "",
            "metadata": {}
        }

        result = self.workflow.invoke(initial_state)
        return result

    def add_documents_to_knowledge_base(self, file_paths: List[str]) -> Dict:
        try:
            documents = self.document_processor.process_multiple_documents(file_paths)

            if not documents:
                return {"success" : False, "message" : "No documents processed"}

            self.vector_store.add_documents(documents)

            return{
                "success" : True,
                "message" : "Documents added to knowledge base",
                "processed_documents" : len(file_paths),
                "retrieved_documents" : len(documents)
            }
        except Exception as e:
            return {"success" : False, "message" : f"Error adding documents: {e}"}