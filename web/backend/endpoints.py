from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline.query_rag import query_rag
from rag_pipeline.model import Model
import traceback


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # ["https://www.hamburg.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Model.init()

class QuestionRequest(BaseModel):
    question: str
    url: str | None = None

@app.post("/api/chat")
async def chat(req: QuestionRequest):
    try:
        answer, sources = query_rag(req.question)
        return { "answer": answer, "sources": sources }
    except Exception as e:
        traceback.print_exc()
        return { "answer": "Ups! Ein Fehler ist aufgetreten. Bitte versuchen Sie es später noch einmal." }