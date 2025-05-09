"""Dieses Script bietet ein CLI zur Bedienung der RAG-Pipeline"""

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from rag_pipeline.model import Model


DB_PATH = "./rag_pipeline/db"

PROMPT_TEMPLATE = """
Du bist ein Chatbot für das Bürger-Service-Center von Hamburg. Beantworte die Frage ausschliesslich basierend auf folgendem Kontext. Wenn der Kontext die Antwort nicht vollständig enthält, antworte nicht:

{context}

---

Nutzer-Query: {question}
"""


"""Lädt die Datenbank"""
def load_db(db_path, embedding_function):
    return Chroma(persist_directory=db_path, embedding_function=embedding_function)

"""Baut den Prompt anhand des PROMPT_TEMPLATE zusammen"""
def build_prompt(query_text, retrieved_sources):
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_sources])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    return prompt

"""Formatiert die übergebenen Quellen"""
def format_sources(results):
    # exact_sources = [(doc.metadata.get("id", None), _score) for doc, _score in results]
    formatted_sources = [{"source": doc.metadata.get("source"), "excerpt": doc.page_content} for doc, _ in results]
    return formatted_sources
    
"""Führt eine Nutzeranfrage aus"""
def query_rag(query_text: str):
    db = load_db(DB_PATH, Model.getEmbeddingFunction())

    retrieved_sources = db.similarity_search_with_score(query_text, k=5)
    prompt = build_prompt(query_text, retrieved_sources)
    response_text = generate_answer(prompt)
    sources = format_sources(retrieved_sources)
    
    return response_text, sources

"""Generiert eine Antwort auf den Prompt"""
def generate_answer(prompt):
    llm = Model.getLLMModel()
    response_text = llm.invoke(prompt)
    return response_text.content

"""CLI-Chat für den Zugriff auf die RAG-Pipeline"""
def main():
    Model.init()

    while True:
        query_text = input("Query: ")
        if query_text == "q" or not query_text:
            break
        response_text, sources = query_rag(query_text)
        print(response_text, sources)


if __name__ == "__main__":
    main()