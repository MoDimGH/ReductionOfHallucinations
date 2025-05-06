"""Dieses Script setzt basierend auf dem Datensatz die Vektordatenbank der RAG-Pipeline auf"""

import argparse
import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from model import Model
from langchain_chroma import Chroma
from math import ceil


DB_PATH = "./db"
DATA_PATH = "../scraping/all_files/"


"""Lädt die Datenbank"""
def load_db():
    return Chroma(persist_directory=DB_PATH, embedding_function=Model.getEmbeddingFunction())


"""Ergänzt, falls nicht schon enthalten, alle Dokumente der angegebenen Directory in die Datenbank"""
def add_files(path_to_data_dir):
    documents = load_documents(path_to_data_dir)
    chunks = split_documents(documents)
    add_to_db(chunks)


"""Lädt die Dokumente in den Programmspeicher"""
def load_documents(path_to_dir):
    md_document_loader = DirectoryLoader(path_to_dir, glob="*.md")
    pdf_document_loader = PyPDFDirectoryLoader(path_to_dir)
    return md_document_loader.load() + pdf_document_loader.load()


"""Unterteilt die angegebenen Dokumente in Abschnitte"""
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


"""Fügt die angegebenen Dokumentenabschnitte zur Chroma-Datenbank hinzu"""
def add_to_db(chunks: list[Document]):
    db = load_db()

    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[])
    print(existing_items)
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        print(f"Adding new documents: {len(new_chunks)}")

        max_batch_size = 5000
        n_batches = ceil(len(new_chunks) / max_batch_size)
        for i in range(n_batches):
            db.add_documents(new_chunks[i * max_batch_size : (i+1) * max_batch_size], ids=new_chunk_ids)
            db.persist()
    else:
        print("No new documents to add")


"""Bestimmt IDs für die angegebenen Dokumentenabschnitte"""
def calculate_chunk_ids(chunks):

    # Beispiel-ID: "personalausweis.md:6:2"
    # Page Source : Page Number : Chunk Index

    prev_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == prev_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        prev_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


"""Löscht die gesamte Datenbank"""
def clear_database():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)


"""Löscht alle Abschnitte des angegebenen Dokuments aus der Datenbank"""
def remove_file(pdf_filename):
    db = load_db()

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])

    to_delete = [doc_id for doc_id in existing_ids if pdf_filename in doc_id]

    if to_delete:
        print(f"Removing {len(to_delete)} document(s) of {pdf_filename}")
        db.delete(to_delete)
        db.persist()
        print("Deletion completed")
    else:
        print("No matching documents found in the database.")


"""Erstellt CLI für die Datenbankerstellung und lädt die Dokumente in die Vektordatenbank"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    Model.init()
    add_files(DATA_PATH)


if __name__ == "__main__":
    main()
