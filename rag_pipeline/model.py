"""Dieses Script liefert eine einheitliche Modells für den Abruf von Dokumenten und die Generierung von Antworten"""

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from rag_pipeline.constants import RETRIEVAL_MODEL, GENERATION_MODEL


class Model:
    llm_model = None
    embedding_model = None

    @classmethod
    def init(cls):
        if not cls.llm_model:
            cls.llm_model = ChatOllama(model=GENERATION_MODEL)
        
        if not cls.embedding_model:
            cls.embedding_model = OllamaEmbeddings(model=RETRIEVAL_MODEL)

    """Liefert eine einheitliche Instanz des LLM-Modells"""
    @classmethod
    def getLLMModel(cls):
        if not cls.llm_model:
            raise Exception("LLM model not initialized")
            
        return cls.llm_model

    """Liefert eine einheitliche Instanz des Embedding-Modells"""
    @classmethod
    def getEmbeddingFunction(cls):
        if not cls.embedding_model:
            raise Exception("Embedding model not initialized")
            
        return cls.embedding_model
