from datasets import load_dataset

amnesty_qa = load_dataset("explodinggradients/amnesty_qa", "english_v2")

amnesty_subset = amnesty_qa["eval"].select(range(2))

from ragas.metrics import answer_relevancy, faithfulness, context_recall, context_precision

from langchain_ollama import ChatOllama
from ragas import evaluate
from langchain_ollama import OllamaEmbeddings


langchain_llm = ChatOllama(model="llama3")
langchain_embeddings = OllamaEmbeddings(model="llama3")

result = evaluate(amnesty_subset, metrics=[
    answer_relevancy, faithfulness, context_recall, context_precision
], llm=langchain_llm, embeddings=langchain_embeddings)