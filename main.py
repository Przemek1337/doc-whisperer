import streamlit as st
import os
from workflows.rag_workflow import RAGWorkflow
from config.settings import settings


def initialize_session_state():
    """Inicjalizuje wszystkie zmienne session state"""
    if 'rag_workflow' not in st.session_state:
        st.session_state.rag_workflow = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []


def main():
    st.set_page_config(
        page_title="Inteligentny Asystent Dokumentów",
        page_icon="📚",
        layout="wide"
    )

    initialize_session_state()

    st.title("📚 Inteligentny Asystent Dokumentów")
    st.markdown("*System RAG do analizy dokumentów z wykorzystaniem OpenAI i LangGraph*")

    if not settings.OPENAI_API_KEY:
        st.error(" Brak klucza OpenAI API! Ustaw OPENAI_API_KEY w pliku .env")
        return

    if st.session_state.rag_workflow is None:
        try:
            with st.spinner("Inicjalizacja systemu RAG..."):
                st.session_state.rag_workflow = RAGWorkflow()
            st.success("✅ System RAG został zainicjalizowany")
        except Exception as e:
            st.error(f"❌ Błąd inicjalizacji: {str(e)}")
            return

    with st.sidebar:
        st.header("📁 Zarządzanie Dokumentami")

        uploaded_files = st.file_uploader(
            "Wybierz dokumenty",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True
        )

        if uploaded_files and st.button("📤 Dodaj do bazy wiedzy"):
            with st.spinner("Przetwarzanie dokumentów..."):

                temp_paths = []
                for uploaded_file in uploaded_files:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    temp_paths.append(temp_path)

                result = st.session_state.rag_workflow.add_documents_to_knowledge_base(temp_paths)

                for temp_path in temp_paths:
                    try:
                        os.remove(temp_path)
                    except:
                        pass

                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])

        st.subheader("📊 Informacje o bazie")
        if st.session_state.rag_workflow is not None:
            try:
                collection_info = st.session_state.rag_workflow.vector_store.get_collection_info()
                if "error" not in collection_info:
                    st.info(f"Dokumenty w bazie: {collection_info['document_count']}")
                else:
                    st.warning("Błąd pobierania informacji o bazie")
            except Exception as e:
                st.warning(f"Błąd: {str(e)}")
        else:
            st.warning("System RAG nie został zainicjalizowany")

    st.header("💬 Zadaj pytanie o swoje dokumenty")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Zadaj pytanie o swoje dokumenty..."):
        if st.session_state.rag_workflow is None:
            st.error("❌ System RAG nie został zainicjalizowany. Odśwież stronę.")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Szukam odpowiedzi w dokumentach..."):
                result = st.session_state.rag_workflow.process_query(prompt)

                response = result["response"]
                st.markdown(response)

                if result["retrieved_documents"]:
                    with st.expander("📖 Źródła informacji"):
                        for i, doc in enumerate(result["retrieved_documents"], 1):
                            source = doc.metadata.get("source", "Nieznane")
                            st.markdown(f"**Źródło {i}:** {source}")
                            st.code(doc.page_content[:200] + "...")

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
