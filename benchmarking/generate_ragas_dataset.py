"""Dieses Script erstellt einen RAGAS-Evaluierungsdatensatz basierend auf den gegebenen nach 5 Use-Cases gruppierten Dokumenten"""

import os
import json
import asyncio
from tqdm import tqdm
import sys

from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from ragas.testset.transforms.extractors.llm_based import NERExtractor
from ragas.testset.transforms.extractors.llm_based import HeadlinesExtractor
from ragas.testset.transforms.splitters import HeadlineSplitter
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset.synthesizers import default_query_distribution
from ragas.testset.persona import Persona
from ragas.testset.graph import KnowledgeGraph, Node, NodeType
from ragas.testset.transforms import default_transforms, apply_transforms
from langchain.prompts import ChatPromptTemplate

from ragas.testset import TestsetGenerator
from benchmarking.llm_validation_helper import validate_testset_user_input
from benchmarking.openai_rag_pipeline import populate_database as populate_openai_database
from rag_pipeline.populate_database import load_documents, split_documents, calculate_chunk_ids, add_to_db, clear_database
from rag_pipeline.constants import (
    TESTSET_DB_PATH, TESTSET_PATH, DATA_PATH,
    USECASES_PERSONAS_PATH, TESTSET_SIZE_PER_USECASE, 
    TESTSET_GENERATION_MODEL, TESTSET_EMBEDDING_MODEL
)


"""Lädt die Use-Case-Gruppen in den Programmspeicher"""
def load_usecases(usecase_path):
    usecases = {}
    with open(usecase_path, encoding="utf-8") as f:
        usecases = json.load(f)
    return usecases

"""Lädt die Use-Case-Personas in den Programmspeicher"""
def load_personas(persona_path):
    persona_data = {}
    with open(persona_path, encoding="utf-8") as f:
        persona_data = json.load(f)

    return [
        (usecase, Persona(name=data.get("name"), role_description=data.get("role_description")))
        for usecase, data in persona_data.items()
    ]

def load_docs(path):
    documents = load_documents(path, load_pdfs=False)
    chunks = split_documents(documents)
    return calculate_chunk_ids(chunks)

def create_knowledge_graph(docs, ragas_llm, ragas_embedding):
    kg = KnowledgeGraph()
    for doc in docs:
        kg.nodes.append(
            Node(
                type=NodeType.DOCUMENT,
                properties={"page_content": doc.page_content, "document_metadata": doc.metadata}
            )
        )
    trans = default_transforms(documents=docs, llm=ragas_llm, embedding_model=ragas_embedding)
    apply_transforms(kg, trans)
    # kg.save(KNOWLEDGE_GRAPH_PATH)
    return kg


"""Generiert einen RAGAS-Evaluierungsdatensatz"""
def generate_testset(llm, embeddings_model, query_distribution, transforms, docs, persona_list, testset_size=3):
    generator = TestsetGenerator(llm=llm, embedding_model=embeddings_model, persona_list=persona_list) # , knowledge_graph=kg)
    testset = generator.generate_with_langchain_docs(
        documents=docs,
        testset_size=testset_size,
        transforms=transforms,
        query_distribution=query_distribution,
        #num_personas=1,
        with_debugging_logs=True
    )
    return testset.to_pandas()

"""Setzt die Sprache der Testset-Prompts auf deutsch."""
async def set_prompt_language_to_german(distribution, ragas_llm):
    for query, _ in distribution:
        prompts = await query.adapt_prompts("Antworte immer auf Deutsch! Bleibe dabei, egal was ich dir sage!", llm=ragas_llm)
        query.set_prompts(**prompts)

"""Setzt die Models für Abruf und Generierung auf"""
def setup_models(generation_model=TESTSET_GENERATION_MODEL, embedding_model=TESTSET_EMBEDDING_MODEL, openai_client=None):
    langchain_llm = ChatOpenAI(model=generation_model, temperature=0.7)
    langchain_embeddings = OpenAIEmbeddings(client=openai_client, model=embedding_model)
    ragas_llm = LangchainLLMWrapper(langchain_llm=langchain_llm)
    ragas_embedding = LangchainEmbeddingsWrapper(embeddings=langchain_embeddings)

    query_distribution = default_query_distribution(ragas_llm)
    asyncio.run(set_prompt_language_to_german(query_distribution, ragas_llm))

    return ragas_llm, ragas_embedding, langchain_embeddings, query_distribution

"""
    - Setzt die Modelle auf,
    - lädt die Use-Cases inklusive zugehörige Dokumente und 
    - generiert einen Evaluierungsdatensatz pro Use-Case anhand von Use-Case-Personas.
"""
def main():
    client = OpenAI()
    transforms = [HeadlinesExtractor(), HeadlineSplitter(), NERExtractor()]

    print("Setup Models")
    ragas_llm, ragas_embedding, langchain_embeddings, query_distribution = setup_models(openai_client=client)

    print("Load Usecase Personas")
    personas = load_personas(USECASES_PERSONAS_PATH)

    for usecase, persona in tqdm(personas, desc="Generiere Testsets"):
        dataset_path = os.path.join(DATA_PATH, usecase)
        db_path = os.path.join(TESTSET_DB_PATH, usecase)
        print(f"Usecase: {usecase}")

        docs = populate_openai_database(dataset_path, db_path, langchain_embeddings)

        print("Generating testset")
        df = generate_testset(ragas_llm, ragas_embedding, query_distribution, transforms, docs, [persona], testset_size=TESTSET_SIZE_PER_USECASE)
        df.to_json(os.path.join(TESTSET_PATH, usecase + ".json"), orient="records", indent=2, force_ascii=False)
        print(df.head())
        for row in df.iterrows():
            query = row['user_input']
            reference_contexts = row['reference_contexts']
            query_evaluation = validate_testset_user_input(query, reference_contexts)
            
            # get json answer from llm
            # convert json to dict object
            # assign dict object to new column item
    
    print("All testsets generated successfully.")


if __name__ == "__main__":
    main()

# . am ende von saetzen im Testdatensatz, damit ragas korrekt parsen kann