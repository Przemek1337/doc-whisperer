from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config.settings import settings
from utils.file_handlers import FileHandler

class DocumentProcessor:
    """
    Converts documents to pieces ready to embed
    """
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.file_handler = FileHandler()
    def process_document(self, file_path: str) -> List[Document]:
        """
        Processes one single document into pieces
        """
        try:
            extracted_data = self.file_handler.extract_text(file_path)

            chunks = self.text_splitter.split_text(extracted_data["text"])

            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source" : extracted_data["filename"],
                        "file_type" : extracted_data["file_type"],
                        "chunk_id" : i,
                        "total_chunks" : len(chunks)
                    }
                )
                documents.append(doc)
            return documents
        except Exception as e:
            raise Exception(f"Error while processing a document {e}")

    def process_multiple_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Processes multiple documents into pieces
        """
        all_documents = []

        for file_path in file_paths:
            try:
                documents = self.process_document(file_path)
                all_documents.extend(documents)
                print(f"Processed: {file_path}, {len(documents)} documents")
            except Exception as e:
                print(f"Error while processing {file_path}: {e}")

        return all_documents