"""Dieses Script beinhaltet Utility-Methoden für die RAG-Pipeline"""

from langchain_chroma import Chroma
from rag_pipeline.model import Model


"""Lädt die Datenbank"""
def load_db(db_path, embedding_function):
    return Chroma(persist_directory=db_path, embedding_function=embedding_function)

"""Erstellt einen Chroma Retriever"""
def create_chroma_retriever(db_path, embedding_model=None, k=5):
    db = load_db(db_path, embedding_model or Model.getEmbeddingFunction())
    return db.as_retriever(search_kwargs={"k": k})