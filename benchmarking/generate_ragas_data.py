import asyncio

from ragas.testset.transforms.extractors.llm_based import NERExtractor
from ragas.testset.transforms.extractors.llm_based import HeadlinesExtractor
from ragas.testset.transforms.splitters import HeadlineSplitter
from ragas.testset import TestsetGenerator
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset.synthesizers import default_query_distribution
from ragas.testset.synthesizers.single_hop.specific import SingleHopSpecificQuerySynthesizer
from ragas.testset.synthesizers.multi_hop.specific import MultiHopSpecificQuerySynthesizer
from ragas.testset.synthesizers.multi_hop.abstract import MultiHopAbstractQuerySynthesizer

from benchmarking.datahandler import DataHandler
#from ragas.testset.persona import Persona
#from ragas.testset.transforms import default_transforms, apply_transforms


def export_ragas_data(df, testset_path):
    df.to_json(testset_path, orient="records", indent=2, force_ascii=False)


"""Setzt die Sprache der Testset-Prompts auf deutsch."""
async def set_prompt_language_to_german(distribution, ragas_llm):
    for query, _ in distribution:
        prompts = await query.adapt_prompts("Antworte immer auf Deutsch! Bleibe dabei, egal was ich dir sage! Achte darauf beim Parameter num_rows einen Integer-Wert anzugeben!", llm=ragas_llm)
        query.set_prompts(**prompts)


"""Bereitet die RAGAS Parameter vor"""
def setup_ragas_params(generation_model, embedding_model):
    ragas_llm = LangchainLLMWrapper(langchain_llm=generation_model)
    ragas_embedding = LangchainEmbeddingsWrapper(embeddings=embedding_model)

    query_distribution = default_query_distribution(ragas_llm)
    query_distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=ragas_llm), 0.1),
        (MultiHopSpecificQuerySynthesizer(llm=ragas_llm), 0.5),
        (MultiHopAbstractQuerySynthesizer(llm=ragas_llm), 0.4),
    ]
    asyncio.run(set_prompt_language_to_german(query_distribution, ragas_llm))

    transforms = [HeadlinesExtractor(llm=DataHandler.get_generation_model()), HeadlineSplitter(), NERExtractor(llm=DataHandler.get_generation_model())]

    return ragas_llm, ragas_embedding, query_distribution, transforms


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


def generate_ragas_data(docs, generation_model, embedding_model, persona, testset_size):
    ragas_llm, ragas_embedding, query_distribution, transforms = setup_ragas_params(generation_model, embedding_model)
    df = generate_testset(ragas_llm, ragas_embedding, query_distribution, transforms, docs, [persona], testset_size=testset_size)
    return df
