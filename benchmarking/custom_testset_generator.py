from ragas.testset import TestsetGenerator
from langchain.schema import Document
from typing import List


class TestsetGenerator_WithFilenames(TestsetGenerator):
    def _get_reference_context_sources(self, docs: List[Document]) -> List[str]:
        sources = []
        for doc in docs:
            doc_id = doc.metadata.get("id", "unknown")
            sources.append(f"[id:{doc_id}] {doc.page_content}")
        return sources

    def generate_with_langchain_docs(self, docs, **kwargs):
        testset = super().generate_with_langchain_docs(docs, **kwargs)

        for sample in testset.samples:
            sample.reference_contexts = self._get_reference_context_sources(sample.reference_contexts)

        return testset
