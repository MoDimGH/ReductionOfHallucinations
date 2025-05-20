"""Dieses Script erstellt einen RAGAS-Evaluierungsdatensatz basierend auf den gegebenen nach 5 Use-Cases gruppierten Dokumenten"""

import os
import json
import asyncio

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset.synthesizers.single_hop.specific import SingleHopSpecificQuerySynthesizer
from ragas.testset.synthesizers.multi_hop.specific import MultiHopSpecificQuerySynthesizer
from ragas.testset.persona import Persona

from benchmarking.custom_testset_generator import TestsetGenerator_WithFilenames
from rag_pipeline.utilities import load_db
from rag_pipeline.model import Model
from rag_pipeline.constants import (
    DB_PATH, TESTSET_PATH, 
    USECASES_PERSONAS_PATH, TESTSET_SIZE_PER_USECASE, 
    TESTSET_MODEL
)


"""Lädt die Use-Case-Gruppen in den Programmspeicher"""
def load_usecases(usecase_path):
    usecases = {}
    with open(usecase_path, encoding="utf-8") as f:
        usecases = json.load(f)
    return usecases

"""Lädt die Use-Case-Personas in den Programmspeicher"""
def load_personas(persona_path):
    personas = {}
    with open(persona_path, encoding="utf-8") as f:
        personas = json.load(f)
    return personas

"""Lädt die angegebenen Dokumente in den Programmspeicher"""
def load_documents(dir: str) -> list[Document]:
    filenames = [os.path.basename(filename) for filename in os.listdir(dir)]

    Model.init()
    db = load_db(DB_PATH, Model.getEmbeddingFunction())
    existing_items = db.get(include=["documents"])

    docs = [
        doc 
        for id, doc in zip(existing_items["ids"], existing_items["documents"]) 
        if any([(filename in id) for filename in filenames])
    ]
    return docs

"""Generiert einen RAGAS-Evaluierungsdatensatz"""
def generate_testset(docs, llm, embeddings_model, distribution, persona_list, testset_size=3):
    generator = TestsetGenerator_WithFilenames(llm=llm, embedding_model=embeddings_model, persona_list=persona_list)
    testset = generator.generate_with_langchain_docs(
        docs[:],
        testset_size=testset_size,
        query_distribution=distribution,
    )
    return testset.to_pandas()

"""Setzt die Sprache der Testset-Prompts auf deutsch."""
async def set_prompt_language_to_german(distribution, ragas_llm):
    for query, _ in distribution:
        prompts = await query.adapt_prompts("Generiere immer auf deutsch!", llm=ragas_llm)
        query.set_prompts(**prompts)

"""Setzt die Models für Abruf und Generierung auf"""
def setup_models(model=TESTSET_MODEL):
    langchain_llm = ChatOllama(model=model)
    langchain_embeddings = OllamaEmbeddings(model=model)
    ragas_llm = LangchainLLMWrapper(langchain_llm=langchain_llm)
    ragas_embedding = LangchainEmbeddingsWrapper(embeddings=langchain_embeddings)

    distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=ragas_llm), 0.6),
        (MultiHopSpecificQuerySynthesizer(llm=ragas_llm), 0.4),
    ]
    asyncio.run(set_prompt_language_to_german(distribution, ragas_llm))

    return ragas_llm, ragas_embedding, distribution

"""
    - Setzt die Modelle auf,
    - lädt die Use-Cases inklusive zugehörige Dokumente und 
    - generiert einen Evaluierungsdatensatz pro Use-Case anhand von Use-Case-Personas.
"""
def main():
    ragas_llm, ragas_embedding, distribution = setup_models()
    usecase_personas = load_personas(USECASES_PERSONAS_PATH)

    for usecase_ix, persona in usecase_personas.items():
        name = persona.get("name")
        role_description = persona.get("role_description")
        reference_dir = persona.get("reference_dir")

        print(f"Generating Testset for usecase {usecase_ix}: \"{name}\"...")

        docs = load_documents(reference_dir)
        persona_list = [
            Persona(
                name=name,
                role_description=role_description
            ),
        ]

        df = generate_testset(docs, ragas_llm, ragas_embedding, distribution, persona_list, testset_size=TESTSET_SIZE_PER_USECASE)
        df.to_json(os.path.join(TESTSET_PATH, os.path.basename(reference_dir) + ".json"), orient="records", indent=2, force_ascii=False)


if __name__ == "__main__":
    main()