"""Dieses Script stellt den Hybrid-Retriever bereit, welcher das dichte und spärliche Abrufen kombiniert"""

from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever
from langchain_chroma import Chroma

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from rag_pipeline.constants import DB_PATH, BM25_INDEX_PATH
from rag_pipeline.utilities import create_chroma_retriever
from rag_pipeline.model import Model

import nltk
from nltk.tokenize import word_tokenize


nltk.download("punkt_tab")


class HybridRetriever:
    hybrid_retriever = None

    """Initialisiert den Retriever"""
    @classmethod
    def init(cls, db_path=DB_PATH):
        Model.init()
        dense_retriever = create_chroma_retriever(db_path, k=5)

        ix = open_dir(BM25_INDEX_PATH)
        sparse_retriever = BM25Retriever(searcher=ix.searcher(), parser=QueryParser("content", ix.schema), k=5, preprocess_func=word_tokenize)

        cls.hybrid_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[0.5, 0.5]
        )
    
    """Gibt die Instanz des Hybrid Retrievers zurück"""
    @classmethod
    def getRetriever(cls):
        if not cls.hybrid_retriever:
            raise Exception("Hybrid Retriever not initialized")
        return cls.hybrid_retriever
