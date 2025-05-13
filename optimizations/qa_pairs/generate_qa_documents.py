"""Dieses Script generiert Frage-Antwort-Abschnitte für jede Dokumentenseite im Datensatz"""

import os
import shutil
from tqdm import tqdm

from langchain.schema.document import Document
from langchain.prompts import ChatPromptTemplate

from rag_pipeline.query_rag import generate_answer
from rag_pipeline.populate_database import load_documents
from rag_pipeline.constants import DATA_PATH, QA_DATA_PATH
from rag_pipeline.model import Model


QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
Erzeugen Sie aus der folgenden Dokumentseite 15 sachliche Frage-Antwort-Paare in der Sprache deutsch, die direkt aus dem Text beantwortet werden können.

Dokumentenseite:
{context}

Frage-Antwort-Paare:
""")


"""Generiert einen Dokumententitel und -inhalt mit einer Frage-Antwort-Liste für die angegebene Dokumentenseite"""
def generate_qa_section_document(document: Document):
    prompt = QA_PROMPT_TEMPLATE.format(context=document.page_content)
    qa_text = generate_answer(prompt)

    source = os.path.basename(document.metadata.get("source"))
    page = document.metadata.get("page") or 0
    qa_id = f"{source}:{page}:qa"

    return qa_id, qa_text


"""Legt den QA_Abschnitt im Dateiverzeichnis ab."""
def save_qa_document(qa_id, qa_text):
    with open(os.path.join(QA_DATA_PATH, qa_id), 'w') as f:
        f.write(qa_text)

"""Löscht bestehende Frage-Antwort-Sections"""
def clean_qa_sections():
    if os.dir.exists(QA_DATA_PATH):
        shutil.rmtree(QA_DATA_PATH)
    os.mkdir(QA_DATA_PATH)

"""Generiert Frage-Antwort-Abschnitte für jede Dokumentenseite des Datensatzes und speichert sie in eigenen Dateien ab"""
def main(reset=False):
    print("Lade Dokumente...")
    documents = load_documents(DATA_PATH)
    print("Dokumente geladen")

    if reset:
        print("Lösche bestehende Frage-Antwort-Abschnitte")
        clean_qa_sections()

    print("Generiere QA-Abschnitt für jede Dokumentenseite...")
    Model.init()
    for page in tqdm(documents):
        qa_id, qa_text = generate_qa_section_document(page)
        save_qa_document(qa_id, qa_text)
        

if __name__ == "__main__":
    main()