import os

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from rag_pipeline.populate_database import load_db
from rag_pipeline.constants import (
    TESTSET_GENERATION_MODEL, TESTSET_EMBEDDING_MODEL, 
    TESTSET_DB_PATH, 
    TESTSET_VALIDATION_QUERY_KW,
    TESTSET_VALIDATION_EXPECTED_ANSWER_KW,
    TESTSET_VALIDATION_REFERENCES_KW,
    TESTSET_HELPER_SOURCES_KW,
    TESTSET_HELPER_ALTERNATIVE_ANSWERS_KW,
    TESTSET_HELPER_ANSWER_EXTRACTIONWISE_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_EXTRACTIONWISE_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_CONTEXTUALLY_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_CONTEXTUALLY_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_CITATIONWISE_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_CITATIONWISE_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_REASONING_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_REASONING_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_SEMANTICALLY_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_SEMANTICALLY_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_STRUCTURALLY_HALLUCINATED_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_STRUCTURALLY_HALLUCINATED_KW,
    TESTSET_HELPER_ANSWER_FACTUALLY_WRONG_MESSAGES_KW,
    TESTSET_HELPER_IS_ANSWER_FACTUALLY_HALLUCINATED_KW,
    TESTSET_HELPER_ALTERNATIVE_QUERIES_KW,
    TESTSET_HELPER_IS_QUERY_SUPPORTED_KW
)

from benchmarking.manual_validation.testset_item import TestsetItem
from benchmarking.manual_validation.io import (
    load_original_testsets,
    load_validated_testsets, save_validated_testsets,
    load_testset_item_template,
    load_helper_data, save_helper_data,
    load_helper_data_item_template
)


class DataHandler:
    dbs = {}
    model = None
    original_testsets = []
    validated_testsets = {}
    helper_data = {}
    testset_item_template = {}
    helper_data_item_template = {}

    @classmethod
    def init(cls):
        if not cls.dbs:
            embedding_model = OllamaEmbeddings(model=TESTSET_EMBEDDING_MODEL)
            for db_path in os.listdir(TESTSET_DB_PATH):
                cls.dbs[os.path.basename(db_path).rstrip(".json")] = load_db(
                    os.path.join(TESTSET_DB_PATH, db_path), embedding_model
                )

        if not cls.model:
            cls.model = ChatOllama(model=TESTSET_GENERATION_MODEL)

        if not cls.original_testsets:
            testsets = load_original_testsets()
            cls.original_testsets = list(testsets.items())

        if not cls.testset_item_template:
            cls.testset_item_template = load_testset_item_template()

        if not cls.helper_data_item_template:
            cls.helper_data_item_template = load_helper_data_item_template()

        if not cls.validated_testsets:
            cls.validated_testsets = load_validated_testsets()
        
        if not cls.helper_data:
            cls.helper_data = load_helper_data()
    

    @classmethod
    def get_db(cls, usecase):
        return cls.dbs.get(usecase)
    
    @classmethod
    def get_testset_usecase(cls, testset_i) -> str:
        return cls.original_testsets[testset_i][0]

    @classmethod
    def get_original_testset_item(cls, testset_i, item_i) -> TestsetItem:
        raw_testset_item = cls.original_testsets[testset_i][1][item_i]
        return TestsetItem(
            raw_testset_item.get(TESTSET_VALIDATION_QUERY_KW), 
            raw_testset_item.get(TESTSET_VALIDATION_EXPECTED_ANSWER_KW), 
            raw_testset_item.get(TESTSET_VALIDATION_REFERENCES_KW)
        )

    @classmethod
    def get_testset_amount(cls) -> int:
        return len(cls.original_testsets)

    @classmethod
    def get_testset_size(cls, testset_i) -> int:
        return len(cls.original_testsets[testset_i])
    
    # Validated Testset -----------------------------------------
    
    @classmethod
    def init_validated_testset_item(cls, usecase, i):
        if usecase not in cls.validated_testsets:
            raise Exception("Invalid Usecase.")
        
        if not cls.validated_testsets.get(usecase).get(str(i)):
            cls.validated_testsets[usecase][str(i)] = cls.validated_testsets
    
        save_validated_testsets(cls.validated_testsets)
    
    @classmethod
    def get_validated_query(cls, usecase, i):
        return cls.validated_testset.get(usecase).get(str(i)).get(TESTSET_VALIDATION_QUERY_KW)
    
    @classmethod
    def get_validated_expected_answer(cls, usecase, i):
        return cls.validated_testset.get(usecase).get(str(i)).get(TESTSET_VALIDATION_EXPECTED_ANSWER_KW)
    
    @classmethod
    def get_validated_references(cls, usecase, i):
        return cls.validated_testset.get(usecase).get(str(i)).get(TESTSET_VALIDATION_REFERENCES_KW)
    
    @classmethod
    def set_validated_query(cls, usecase, i, query):
        cls.validated_testset[usecase][str(i)][TESTSET_VALIDATION_QUERY_KW] = query
        save_validated_testsets(cls.validated_testset)
    
    @classmethod
    def set_validated_expected_answer(cls, usecase, i, validated_answer):
        cls.validated_testset[usecase][str(i)][TESTSET_VALIDATION_EXPECTED_ANSWER_KW] = validated_answer
        save_validated_testsets(cls.validated_testset)
    
    @classmethod
    def set_validated_references(cls, usecase, i, validated_ids):
        cls.validated_testset[usecase][str(i)][TESTSET_VALIDATION_REFERENCES_KW] = validated_ids
        save_validated_testsets(cls.validated_testset)

    # Helper Data --------------------------------------------------------------

    @classmethod
    def init_helper_data_item(cls, usecase, i):
        if usecase not in cls.helper_data:
            raise Exception("Invalid Usecase.")
        
        if not cls.helper_data.get(usecase).get(str(i)):
            cls.helper_data[usecase][str(i)] = cls.helper_data_item_template
        
        save_helper_data(cls.helper_data)
    
    @classmethod
    def get_query_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_QUERY_SUPPORTED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ALTERNATIVE_QUERIES_KW)
        )

    @classmethod
    def get_factual_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_FACTUALLY_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_FACTUALLY_WRONG_MESSAGES_KW)
        )
    
    @classmethod
    def get_structural_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_STRUCTURALLY_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_STRUCTURALLY_HALLUCINATED_MESSAGES_KW)
        )

    @classmethod
    def get_semantic_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_SEMANTICALLY_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_SEMANTICALLY_HALLUCINATED_MESSAGES_KW)
        )

    @classmethod
    def get_reasoning_error_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_REASONING_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_REASONING_HALLUCINATED_MESSAGES_KW)
        )
    
    @classmethod
    def get_citation_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_CITATIONWISE_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_CITATIONWISE_HALLUCINATED_MESSAGES_KW)
        )
    
    @classmethod
    def get_contextual_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_CONTEXTUALLY_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_CONTEXTUALLY_HALLUCINATED_MESSAGES_KW)
        )
    
    @classmethod
    def get_extraction_hallucination_check(cls, usecase, i):
        return (
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_IS_ANSWER_EXTRACTIONWISE_HALLUCINATED_KW),
            cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ANSWER_EXTRACTIONWISE_HALLUCINATED_MESSAGES_KW)
        )
    
    @classmethod
    def get_alternative_answers(cls, usecase, i):
        return cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_ALTERNATIVE_ANSWERS_KW)

    @classmethod
    def get_get_sources(cls, usecase, i):
        return cls.helper_data.get(usecase).get(str(i)).get(TESTSET_HELPER_SOURCES_KW)
    
    @classmethod
    def set_query_check(cls, usecase, i, isQuerySupported, alternativeQueries):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_QUERY_SUPPORTED_KW] = isQuerySupported
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ALTERNATIVE_QUERIES_KW] = alternativeQueries
        save_helper_data(cls.helper_data)

    @classmethod
    def set_factual_hallucination_check(cls, usecase, i, isAnswerFactuallyHallucinated, answerFactuallyWrongMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_FACTUALLY_HALLUCINATED_KW] = isAnswerFactuallyHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_FACTUALLY_WRONG_MESSAGES_KW] = answerFactuallyWrongMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_structural_hallucination_check(cls, usecase, i, isAnswerStructurallyHallucinated, answerStructurallyHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_STRUCTURALLY_HALLUCINATED_KW] = isAnswerStructurallyHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_STRUCTURALLY_HALLUCINATED_MESSAGES_KW] = answerStructurallyHallucinatedMessages
        save_helper_data(cls.helper_data)

    @classmethod
    def set_semantic_hallucination_check(cls, usecase, i, isAnswerSemanticallyHallucinated, answerSemanticallyHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_SEMANTICALLY_HALLUCINATED_KW] = isAnswerSemanticallyHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_SEMANTICALLY_HALLUCINATED_MESSAGES_KW] = answerSemanticallyHallucinatedMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_reasoning_error_hallucination_check(cls, usecase, i, isAnswerReasoningHallucinated, answerReasoningHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_REASONING_HALLUCINATED_KW] = isAnswerReasoningHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_REASONING_HALLUCINATED_MESSAGES_KW] = answerReasoningHallucinatedMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_citation_hallucination_check(cls, usecase, i, isAnswerCitationwiseHallucinated, answerCitationwiseHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_CITATIONWISE_HALLUCINATED_KW] = isAnswerCitationwiseHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_CITATIONWISE_HALLUCINATED_MESSAGES_KW] = answerCitationwiseHallucinatedMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_contextual_hallucination_check(cls, usecase, i, isAnswerContextuallyHallucinated, answerContextuallyHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_CONTEXTUALLY_HALLUCINATED_KW] = isAnswerContextuallyHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_CONTEXTUALLY_HALLUCINATED_MESSAGES_KW] = answerContextuallyHallucinatedMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_extraction_hallucination_check(cls, usecase, i, isAnswerExtractionwiseHallucinated, answerExtractionwiseHallucinatedMessages):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_IS_ANSWER_EXTRACTIONWISE_HALLUCINATED_KW] = isAnswerExtractionwiseHallucinated
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ANSWER_EXTRACTIONWISE_HALLUCINATED_MESSAGES_KW] = answerExtractionwiseHallucinatedMessages
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_alternative_answers(cls, usecase, i, alternativeAnswers):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_ALTERNATIVE_ANSWERS_KW] = alternativeAnswers
        save_helper_data(cls.helper_data)
    
    @classmethod
    def set_sources(cls, usecase, i, sources):
        cls.helper_data[usecase][str(i)][TESTSET_HELPER_SOURCES_KW] = sources
        save_helper_data(cls.helper_data)