from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document
from langchain_chroma import Chroma


class ScoreThresholdingRetriever(BaseRetriever):
    def __init__(self, chroma_db: Chroma, score_threshold: float):
        super.__init__()
        self.chroma_db = chroma_db
        self.score_threshold = score_threshold

    def invoke(self, query: str) -> list[Document]:
        results = self.chroma_db.similarity_search_with_score(query)
        return [doc for doc, score in results if score >= self.score_threshold]
