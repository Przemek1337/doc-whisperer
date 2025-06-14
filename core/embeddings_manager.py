from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from config.settings import settings

class EmbeddingsManager:
    """
    Manages creating and handling embeddings
    """
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model = settings.EMBEDDING_MODEL,
            openai_api_key = settings.OPENAI_API_KEY
        )

    def create_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """
        Creates embeddings for list of documents
        """
        try:
            texts = [doc.page_content for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            raise Exception(f"[EMBEDDER] Failed to embed documents: {e}")

    def create_query_embedding(self, query: str) -> List[float]:
        """
        Creates embedding for query
        """
        try:
            return self.embeddings.embed_query(query)
        except Exception as e:
            raise Exception(f"[EMBEDDER] Failed to embed query: {e}")