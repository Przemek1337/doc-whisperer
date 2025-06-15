# doc-whisperer
Doc Whisperer is a Streamlit-based AI app that analyzes and summarizes documents (PDF, DOCX) using LangChain, OpenAI models, and local embeddings via ChromaDB. Just drop a file and get instant insights.

Create .env file in main project directory:
```aiignore
OPENAI_API_KEY=key
VECTOR_DB_PATH=./vector_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```
Installation
```aiignore
git clone https://github.com/yourname/doc-whisperer.git

cd doc-whisperer

uv venv
uv pip install

uv run streamlit run main.py
```