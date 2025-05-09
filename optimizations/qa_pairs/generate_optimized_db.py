"""Dieses Script erstellt eine optimierte Datenbank, indem es zu jeder Dokumentenseite im Datensatz zusätzlich eine Frage-Antwort-List generiert, um den Abruf-Prozess zu verbessern."""

import os
import shutil
from langchain.schema.document import Document
from langchain.prompts import ChatPromptTemplate

from rag_pipeline.model import Model
from rag_pipeline.populate_database import load_documents, split_documents, add_to_db
from rag_pipeline.query_rag import generate_answer


OPTIMIZED_DB_PATH = "./optimizations/qa_pairs/db"
DATASET_PATH = "./scraping/all_files"

QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
Erzeugen Sie aus der folgenden Dokumentseite 15 sachliche Frage-Antwort-Paare, die direkt aus dem Text beantwortet werden können.

Dokumentenseite:
{context}

Frage-Antwort-Paare:
""")


"""Teilt eine Dokumentenseite in Abschnitte auf"""
def split_document_page(document: Document):
    chunks = split_documents([document])
    
    for i, chunk in enumerate(chunks):
        chunk.metadata["id"] += f":{i}"
    
    return chunks

"""Generiert ein Dokument mit einer Frage-Antwort-Liste für die angegebene Dokumentenseite"""
def generate_qa_section_document(document: Document):
    prompt = QA_PROMPT_TEMPLATE.format(context=document.page_content)
    qa_text = generate_answer(prompt)

    source = document.metadata.get("source")
    page = document.metadata.get("page") or 0
    qa_id = f"{source}:{page}:qa"

    return Document(page_content=qa_text, metadata={"source": source, "id": qa_id}) 

"""Generiert ein Dokument mit einer Frage-Antwort-Sammlung für je einen der angegebenen Dokumentenseiten."""
def generate_qa_section_chunks_for_each_page(page_documents: list[Document]):
    qa_chunks = []
    for page in page_documents[5]:
        qa_section_document = generate_qa_section_document(page)
        new_qa_chunks = split_document_page(qa_section_document)
        qa_chunks.extend(new_qa_chunks)

""" 
    - Lädt die Dokumente aus dem Datensatz in den Programmspeicher, 
    - generiert Frage-Antwort-Abschnitte zu jeder Dokumentenseite und 
    - speichert alles in einer Datenbank ab.
"""
def main():
    print("Lade Dokumente...")
    documents = load_documents(DATASET_PATH)
    print("Dokumente erfolgreich geladen")

    print("Entferne bestehende Datenbank (falls vorhanden)")
    if os.path.exists(OPTIMIZED_DB_PATH):
        shutil.rmtree(OPTIMIZED_DB_PATH)

    print("Erstelle Datenbank mit geladenen Dokumenten...")
    chunks = split_documents(documents)
    add_to_db(chunks, OPTIMIZED_DB_PATH)

    Model.init()
    print("Generiere Frage-Antwort-Abschnitte")
    qa_documents = generate_qa_section_chunks_for_each_page(documents)
    print("Füge Frage-Antwort-Abschnitte zur Datenbank hinzu")
    add_to_db(qa_documents, OPTIMIZED_DB_PATH)

    print("Datenbank erfolgreich aufgesetzt!")


if __name__ == "__main__":
    main()
