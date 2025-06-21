import os
from openai import OpenAI

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from rag_pipeline.populate_database import load_db
from rag_pipeline.constants import (
    TESTSET_GENERATION_MODEL, TESTSET_EMBEDDING_MODEL, 
    TESTSET_DB_PATH,
    TESTSET_HALLUCINATIONS_ART_KW,
    TESTSET_GENERIERTE_QUERY_KW,
    TESTSET_PROVOKATIONS_ERLAEUTERUNG_KW,
    TESTSET_GROUND_TRUTH_ANTWORT_KW,
    TESTSET_ABGERUFENE_QUELLEN_KW
)

from benchmarking.testset_item import TestsetItem
from benchmarking.io import (
    load_original_testsets,
    load_validated_testsets, save_validated_testsets
)


class DataHandler:
    openai_client = None
    dbs = {}
    generation_model = None
    embedding_model = None
    original_testsets = []
    validated_testsets = {}

    @classmethod
    def init(cls, reinit=False):
        if reinit or not cls.openai_client:
            cls.openai_client = OpenAI()

        if reinit or not cls.embedding_model:
            cls.embedding_model = OpenAIEmbeddings(model=TESTSET_EMBEDDING_MODEL)

        if reinit or not cls.dbs:
            for db_path in os.listdir(TESTSET_DB_PATH):
                cls.dbs[os.path.splitext(os.path.basename(db_path))[0]] = load_db(
                    os.path.join(TESTSET_DB_PATH, db_path), cls.embedding_model
                )

        if reinit or not cls.generation_model:
            cls.generation_model = ChatOpenAI(model=TESTSET_GENERATION_MODEL)
        
        if reinit or not cls.original_testsets:
            testsets = load_original_testsets()
            cls.original_testsets = list(testsets.items())

        if reinit or not cls.validated_testsets:
            cls.validated_testsets = load_validated_testsets()
    

    @classmethod
    def get_openai_client(cls):
        return cls.openai_client

    @classmethod
    def get_db(cls, usecase):
        return cls.dbs.get(usecase)
    
    @classmethod
    def get_embedding_model(cls):
        return cls.embedding_model
    
    @classmethod
    def get_generation_model(cls):
        return cls.generation_model
    
    @classmethod
    def get_testset_usecase(cls, testset_i) -> str:
        return cls.original_testsets[testset_i][0]

    @classmethod
    def get_original_testset_item(cls, testset_i, item_i) -> TestsetItem:
        raw_item = cls.original_testsets[testset_i][1][item_i]
        return TestsetItem(
            raw_item.get(TESTSET_HALLUCINATIONS_ART_KW), 
            raw_item.get(TESTSET_GENERIERTE_QUERY_KW), 
            raw_item.get(TESTSET_PROVOKATIONS_ERLAEUTERUNG_KW),
            raw_item.get(TESTSET_GROUND_TRUTH_ANTWORT_KW),
            raw_item.get(TESTSET_ABGERUFENE_QUELLEN_KW)
        )

    @classmethod
    def get_testset_amount(cls) -> int:
        return len(cls.original_testsets)

    @classmethod
    def get_testset_size(cls, testset_i) -> int:
        return len(cls.original_testsets[testset_i][1])
    
    # Validated Testset -----------------------------------------
    
    @classmethod
    def get_validated_testset_item(cls, usecase, i):
        if usecase not in cls.validated_testsets:
            raise Exception(f"Invalid Usecase \"{ usecase }\".")
        
        if not cls.validated_testsets.get(usecase).get(str(i)):
            return None
        
        raw_item = cls.validated_testsets.get(usecase).get(str(i))

        return TestsetItem(
            raw_item.get(TESTSET_HALLUCINATIONS_ART_KW), 
            raw_item.get(TESTSET_GENERIERTE_QUERY_KW), 
            raw_item.get(TESTSET_PROVOKATIONS_ERLAEUTERUNG_KW),
            raw_item.get(TESTSET_GROUND_TRUTH_ANTWORT_KW),
            raw_item.get(TESTSET_ABGERUFENE_QUELLEN_KW)
        )
    
    @classmethod
    def save_validated_testset_item(cls, usecase, i, item):
        if usecase not in cls.validated_testsets:
            raise Exception(f"Invalid Usecase \"{ usecase }\".")
        
        cls.validated_testsets[usecase][str(i)] = {}
        cls.validated_testsets[usecase][str(i)][TESTSET_HALLUCINATIONS_ART_KW] = item.halluzinations_art
        cls.validated_testsets[usecase][str(i)][TESTSET_GENERIERTE_QUERY_KW] = item.generierte_query
        cls.validated_testsets[usecase][str(i)][TESTSET_PROVOKATIONS_ERLAEUTERUNG_KW] = item.provokations_erlaeuterung
        cls.validated_testsets[usecase][str(i)][TESTSET_GROUND_TRUTH_ANTWORT_KW] = item.generierte_ground_truth_antwort
        cls.validated_testsets[usecase][str(i)][TESTSET_ABGERUFENE_QUELLEN_KW] = item.abgerufene_quellen

        save_validated_testsets(cls.validated_testsets)