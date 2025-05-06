"""Dieses Script liefert eine einheitliche Embedding-Function"""

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings


class Model:
    MODEL = "llama3"
    llm_model = None
    embedding_model = None

    @classmethod
    def init(cls):
        if not cls.llm_model:
            cls.llm_model = ChatOllama(model=cls.MODEL)
        
        if not cls.embedding_model:
            cls.embedding_model = OllamaEmbeddings(model=cls.MODEL)

    @classmethod
    def getLLMModel(cls):
        if not cls.llm_model:
            raise Exception("LLM Model not initialized")
            
        return cls.llm_model

    @classmethod
    def getEmbeddingFunction(cls):
        if not cls.embedding_model:
            raise Exception("Embedding model not initialized")
            
        return cls.embedding_model
    

"""Liefert eine einheitliche Embedding-Function mit dem Modell 'llama3'"""
def get_embedding_function():
    return OllamaEmbeddings(model="llama3")
