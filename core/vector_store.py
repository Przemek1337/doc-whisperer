import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document
from config.settings import settings
from core.embeddings_manager import EmbeddingsManager
from typing import List

class VectorStore:
    """Zarządza bazą wektorową do przechowywania i wyszukiwania dokumentów"""

    def __init__(self, collection_name: str = "documents"):
        self.embeddings_manager = EmbeddingsManager()
        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Pobiera lub tworzy kolekcję w bazie wektorowej"""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(name=self.collection_name)

    def add_documents(self, documents: List[Document]) -> None:
        """Dodaje dokumenty do bazy wektorowej"""
        try:

            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [f"{doc.metadata.get('source', 'unknown')}_{doc.metadata.get('chunk_id', i)}"
                   for i, doc in enumerate(documents)]

            embeddings = self.embeddings_manager.create_embeddings(documents)

            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            print(f"✅ Dodano {len(documents)} dokumentów do bazy wektorowej")

        except Exception as e:
            raise Exception(f"Błąd podczas dodawania dokumentów do bazy: {str(e)}")

    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Wyszukuje najbardziej podobne dokumenty"""
        if k is None:
            k = settings.TOP_K_DOCUMENTS

        try:

            query_embedding = self.embeddings_manager.create_query_embedding(query)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )

            documents = []
            for i in range(len(results['documents'][0])):
                doc = Document(
                    page_content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i]
                )
                documents.append(doc)

            return documents

        except Exception as e:
            raise Exception(f"Błąd podczas wyszukiwania: {str(e)}")

    def get_collection_info(self) -> dict:
        """Zwraca informacje o kolekcji - POPRAWIONA IMPLEMENTACJA"""
        try:

            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count
            }
        except Exception as e:
            return {"error": str(e)}
