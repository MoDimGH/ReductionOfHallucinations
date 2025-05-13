"""Dieses Script beinhaltet Utility-Methoden für die RAG-Pipeline"""

from langchain_chroma import Chroma


"""Lädt die Datenbank"""
def load_db(db_path, embedding_function):
    return Chroma(persist_directory=db_path, embedding_function=embedding_function)
