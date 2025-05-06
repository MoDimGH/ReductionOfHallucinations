"""Dieses Script erstellt einen RAGAS-Evaluierungsdatensatz basierend auf den gegebenen nach 5 Use-Cases gruppierten Dokumenten"""

import os
import pypandoc
from langchain.schema import Document
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset import TestsetGenerator
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from ragas.testset.synthesizers.single_hop.specific import SingleHopSpecificQuerySynthesizer
from ragas.testset.persona import Persona
import json
import asyncio


INPUT_DIR = "../scraping/all_files"
OUTPUT_DIR = "./testsets"

PATH_TO_USE_CASES = "./use_cases.json"
USECASE_SONSTIGES_KEYWORD = "sonstiges"
PATH_TO_USE_CASES_PERSONAS = "./use_case_personas.json"

TESTSET_SIZE = 50
MODEL = "mistral-nemo"


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
def load_documents(filenames):
    docs = []
    for i, filename in enumerate(filenames):
        if i > 5: break
        path = os.path.join(INPUT_DIR, filename)
        text = pypandoc.convert_file(path, 'plain')[:1000]
        if len(text.strip()) < 300:
            continue
        docs.append(Document(page_content=text, metadata={"source": path}))
    
    return docs

"""Generiert einen RAGAS-Evaluierungsdatensatz"""
def generate_testset(docs, llm, embeddings_model, distribution, persona_list, testset_size=3):
    generator = TestsetGenerator(llm=llm, embedding_model=embeddings_model, persona_list=persona_list)
    testset = generator.generate_with_langchain_docs(
        docs[:],
        testset_size=testset_size,
        query_distribution=distribution,
    )
    return testset.to_pandas()

"""Setzt die Models für Abruf und Generierung auf"""
def setup_models(model=MODEL):
    langchain_llm = ChatOllama(model=model)
    langchain_embeddings = OllamaEmbeddings(model=model)
    ragas_llm = LangchainLLMWrapper(langchain_llm=langchain_llm)
    ragas_embedding = LangchainEmbeddingsWrapper(embeddings=langchain_embeddings)

    distribution = [(SingleHopSpecificQuerySynthesizer(llm=ragas_llm), 1.0)]

    async def set_prompts_for_distribution():
        for query, _ in distribution:
            prompts = await query.adapt_prompts("Generiere immer auf deutsch!", llm=ragas_llm)
            query.set_prompts(**prompts)
    asyncio.run(set_prompts_for_distribution())

    return ragas_llm, ragas_embedding, distribution


"""
    - Setzt die Modelle auf,
    - lädt die Use-Cases inklusive zugehörige Dokumente und 
    - generiert einen Evaluierungsdatensatz pro Use-Case anhand von Use-Case-Personas.
"""
def main():
    ragas_llm, ragas_embedding, distribution = setup_models()
    personas = load_personas(PATH_TO_USE_CASES_PERSONAS)
    usecases = load_usecases(PATH_TO_USE_CASES)

    for i, (usecase, filenames) in enumerate(usecases.items()):
        if usecase == USECASE_SONSTIGES_KEYWORD:
            continue

        print(f"Generating Testset for usecase {usecase}...")

        docs = load_documents(filenames)
        persona_list = [
            Persona(
                name=personas[str(i)]["name"],
                role_description=personas[str(i)]["role_description"]
            ),
        ]

        df = generate_testset(docs, ragas_llm, ragas_embedding, distribution, persona_list, testset_size=TESTSET_SIZE)
        df.to_json(os.path.join(OUTPUT_DIR, usecase + ".json"), orient="records", indent=2, force_ascii=False)


if __name__ == "__main__":
    main()