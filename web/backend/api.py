"""Dieses Script stellt die REST-API für die Kommunikation mit der RAG-Pipeline aus dem Netz zur Verfügung"""

import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_core.retrievers import BaseRetriever

from rag_pipeline.query_rag import query_rag
from rag_pipeline.model import Model
from rag_pipeline.utilities import create_chroma_retriever
from rag_pipeline.constants import DB_PATH


"""Interface für eine API-Anfrage"""
class QuestionRequest(BaseModel):
    question: str
    url: str | None = None


class API():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # ["https://www.hamburg.de"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    rag_retriever = None

    """Initialisiert die Web-API"""
    @classmethod
    def init(cls, rag_retriever: BaseRetriever=None):
        Model.init()
        cls.rag_retriever = rag_retriever or create_chroma_retriever(DB_PATH)

    """Liefert die FastAPI Instanz"""
    @classmethod
    def getApp(cls):
        if not cls.app:
            raise Exception("API not initialized")
        return cls.app

    """API-Endpunkt für die Kommunikation mit der RAG-Pipeline"""
    @app.post("/api/chat")
    async def chat(req: QuestionRequest):
        try:
            answer, sources = query_rag(req.question, retriever=API.rag_retriever)
            return { "answer": answer, "sources": sources }
        except Exception as e:
            traceback.print_exc()
            return { "answer": "Ups! Ein Fehler ist aufgetreten. Bitte versuchen Sie es später noch einmal." }