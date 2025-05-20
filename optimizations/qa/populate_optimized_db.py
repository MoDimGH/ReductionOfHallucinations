"""Dieses Script fügt den herkömmlichen Datensatz inkl. der generierten Frage-Antwort-Abschnitten für jede Dokumentenseite zu einer optimierten Datenbank hinzu um den Abruf-Prozess zu verbessern."""

import os
import shutil

from rag_pipeline.model import Model
from rag_pipeline.populate_database import load_documents, split_documents, add_to_db, calculate_chunk_ids
from rag_pipeline.constants import DATA_PATH, OPTIMIZED_DB_PATH, QA_DATA_PATH


"""Löscht die bestehende Datenbank"""
def clean_db():
    if os.path.exists(OPTIMIZED_DB_PATH):
        shutil.rmtree(OPTIMIZED_DB_PATH)

""" 
    Lädt die Dokumente aus dem Standard-Datensatz und dem QA-Datensatz in den Programmspeicher und fügt die Dokumente zur optimierten Datenbank hinzu.
"""
def main(reset=False):
    print("Lade Dokumente...")
    data_docs = load_documents(DATA_PATH)
    qa_docs = load_documents(QA_DATA_PATH, "*")
    documents = data_docs + qa_docs
    print(f"Dokumente erfolgreich geladen ({len(data_docs)} + {len(qa_docs)})")

    if reset:
        print("Entferne die bestehende Datenbank")
        clean_db()

    Model.init()
    
    print("Update die Datenbank mit geladenen Dokumenten...")
    chunks = split_documents(documents)
    chunks_with_ids = calculate_chunk_ids(chunks)
    add_to_db(chunks_with_ids, OPTIMIZED_DB_PATH)

    print("Dokumente erfolgreich zur Datenbank hinzugefügt!")


if __name__ == "__main__":
    main()
