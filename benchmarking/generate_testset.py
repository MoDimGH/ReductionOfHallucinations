"""Dieses Script erstellt einen RAGAS-Evaluierungsdatensatz basierend auf den gegebenen nach 5 Use-Cases gruppierten Dokumenten"""

import os
import json
from tqdm import tqdm
import re

from ragas.testset.persona import Persona

from benchmarking.utilities import get_usecase_dataset_share
from benchmarking.generate_ragas_data import generate_ragas_data, export_ragas_data
from benchmarking.datahandler import DataHandler
from rag_pipeline.populate_database import clear_database, add_files, load_documents, split_documents, calculate_chunk_ids, add_to_db
from rag_pipeline.utilities import create_chroma_retriever
from rag_pipeline.constants import (
    TESTSET_DB_PATH, TESTSET_PATH, DATA_PATH,
    USECASES_PERSONAS_PATH, TESTSET_SIZE
)


"""Lädt die Use-Case-Personas in den Programmspeicher"""
def load_personas(persona_path):
    persona_data = {}
    with open(persona_path, encoding="utf-8") as f:
        persona_data = json.load(f)

    return [
        (
            usecase, 
            Persona(name=data.get("name"), role_description=data.get("role_description"))
        )
        for usecase, data in persona_data.items()
    ]

def clean_markdown(content):
    # Convert H1 Setext-style (underlined with '=') to H1 Atx-style
    content = re.sub(r'([^\n]+)\n[=]+', r'# \1', content)

    # Convert H2 Setext-style (underlined with '-') to H2 Atx-style
    content = re.sub(r'([^\n]+)\n[-]+', r'## \1', content)

    # Remove excessive whitespace and empty lines
    content = re.sub(r'\n\s*\n', '\n\n', content)

    # Remove sections with no content (e.g., "Fristen", "Rechtsbehelf")
    content = re.sub(r'###\s+[A-Za-zäöüÄÖÜß\s]+(\n\s*)*###\s*$', '', content)

    # Normalize headings (e.g., ensure there's one empty line before headings)
    content = re.sub(r'([^\n])\n(#)', r'\1\n\n\2', content)  # Make sure headings aren't stuck to previous text

    return content


def create_db(dataset_path, db_path, embedding_model):
    print("Loading documents")
    documents = load_documents(dataset_path)
    print(f"Loaded documents successfully ({len(documents)})")

    for doc in documents:
        doc.page_content = clean_markdown(doc.page_content)

    print("Splitting documents into chunks")
    chunks = split_documents(documents)

    print("Adding chunks to database")
    chunks_with_ids = calculate_chunk_ids(chunks)

    add_to_db(chunks_with_ids, db_path=db_path, embedding_model=embedding_model)

    return chunks_with_ids


"""
    - Setzt die Modelle auf,
    - lädt die Use-Cases inklusive zugehörige Dokumente und 
    - generiert einen Evaluierungsdatensatz pro Use-Case anhand von Use-Case-Personas.
"""
def main():
    DataHandler.init()
    generation_model = DataHandler.get_generation_model()
    embedding_model = DataHandler.get_embedding_model()
    
    print("Load Usecase Personas")
    personas = load_personas(USECASES_PERSONAS_PATH)

    for usecase, persona in tqdm(personas, desc="Generiere Testsets"):
        if usecase == "meldebescheinigung":
            continue
        dataset_path = os.path.join(DATA_PATH, usecase)
        db_path = os.path.join(TESTSET_DB_PATH, usecase)
        testset_path = os.path.join(TESTSET_PATH, usecase + ".json")
        print(f"Usecase: {usecase}")

        print(f"Populating Advanced Database")
        clear_database(db_path)
        docs = create_db(dataset_path, db_path, embedding_model)
        print("Successfully Populated Database")

        print("Generating testset")
        testset_size = TESTSET_SIZE * get_usecase_dataset_share(usecase)
        df = generate_ragas_data(docs, generation_model, embedding_model, persona, testset_size)
        print("Testset generated successfully")

        print("Adding reference contexts from RAG extraction")
        retriever = create_chroma_retriever(db_path, embedding_model)
        for row in df.iterrows():
            user_input = row['user_input']
            additional_reference_contexts = [doc.page_content for doc in retriever.invoke(user_input)]
            row['additional_reference_contexts'] = additional_reference_contexts
        
        export_ragas_data(df, testset_path)
    
    print("All testsets generated successfully.")


if __name__ == "__main__":
    main()

# . am ende von saetzen im Testdatensatz, damit ragas korrekt parsen kann