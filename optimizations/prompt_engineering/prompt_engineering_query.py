from langchain.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever

from rag_pipeline.query_rag import generate_answer, format_sources

PROMPT_TEMPLATE = """
Du bist ein Chatbot für das Bürger-Service-Center von Hamburg. Beantworte die Frage ausschliesslich basierend auf folgendem Kontext. Wenn der Kontext die Antwort nicht vollständig enthält, antworte nicht:

{context}

---

Nutzer-Query: {question}

---

Gehe bei deiner Antwort Schritt für Schritt vor.
"""

PROMPT_TEMPLATE_FOR_CHECKING = """
Du bist ein Chatbot für das Bürger-Service-Center von Hamburg. Deine Aufgabe war es, die Frage des Nutzers ausschliesslich basierend auf folgendem Kontext zu beantworten. Wenn der Kontext die Antwort nicht vollständig enthält, war nicht zu antworten:

{context}

---

Nutzer-Query: {question}

---

Deine Antwort: {answer}

---

Prüfe, ob deine ursprüngliche Antwort korrekt ist und in keinster Weise Halluziniert ist. Gib eine korrekte, eventuell überarbeitete Antwort zurück.
Gehe bei deiner Antwort Schritt für Schritt vor.

Korrekte Antwort:
"""


"""Baut den Prompt anhand des PROMPT_TEMPLATE zusammen"""
def build_prompt(query_text, retrieved_sources):
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_sources])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    return prompt


"""Baut den Prompt anhand des PROMPT_TEMPLATE_FOR_CHECKING zusammen"""
def build_prompt_for_checking(query_text, generated_answer, retrieved_sources):
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_sources])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE_FOR_CHECKING)
    prompt = prompt_template.format(context=context_text, question=query_text, answer=generated_answer)
    return prompt


"""Führt eine Nutzeranfrage aus"""
def query_rag(query_text: str, retriever: BaseRetriever):
    
    retrieved_sources = retriever.invoke(query_text)
    #print(retrieved_sources)
    prompt = build_prompt(query_text, retrieved_sources)
    response_text = generate_answer(prompt)
    prompt_for_checking = build_prompt_for_checking(query_text, response_text, retrieved_sources)
    final_response_text = generate_answer(prompt_for_checking)

    sources = format_sources(retrieved_sources)
    
    return final_response_text, sources