"""Dieses Script enthält für die Anwendung wichtige Konstanten"""

# Databases
DB_PATH = "./rag_pipeline/db"
OPTIMIZED_DB_PATH = "./optimizations/qa/db"
BM25_INDEX_PATH = "./optimizations/hybrid_search/bm25_index"

# Dataset constants
DATA_PATH = "./scraping/dataset/"
DATASET_SOURCES_PATH = "./scraping/dataset_sources.json"
SCRAPED_URLS_FILE = './scraping/urls_to_scrape.json'
SCRAPED_BROKEN_LINKS_FILE = './scraping/broken_links.json'

# Testset constants
TESTSET_PATH = "./benchmarking/testset"
TESTSET_DB_PATH = "./benchmarking/dbs"
USECASES_PERSONAS_PATH = "./benchmarking/use_case_personas.json"
# KNOWLEDGE_GRAPH_PATH = './benchmarking/knowledge_graph.json'
TESTSET_TEST_ITEM_TEMPLATE_PATH = './benchmarking/manual_validation/data/test_item_template.json'
TESTSET_VALIDATED_PATH = './benchmarking/manual_validation/data/validated_testset.json'
TESTSET_HELPER_DATA = './benchmarking/manual_validation/data/generated_helper_data.json'
TESTSET_HELPER_DATA_ITEM_TEMPLATE_PATH = './benchmarking/manual_validation/data/helper_data_item_template.json'

TESTSET_SIZE_PER_USECASE = 50
TESTSET_GENERATION_MODEL = "gpt-4.1"  # "mistral-nemo"
TESTSET_EMBEDDING_MODEL = "text-embedding-ada-002"

TESTSET_ORIGINAL_QUERY_KW = "user_input"
TESTSET_ORIGINAL_EXPECTED_ANSWER_KW = "reference"
TESTSET_ORIGINAL_REFERENCES_KW = "reference_contexts"

TESTSET_VALIDATION_QUERY_KW = "user_input"
TESTSET_VALIDATION_EXPECTED_ANSWER_KW = "expected_answer"
TESTSET_VALIDATION_REFERENCES_KW = "references"

TESTSET_HELPER_IS_QUERY_SUPPORTED_KW = "isQuerySupported"
TESTSET_HELPER_ALTERNATIVE_QUERIES_KW = "alternativeQueries"
TESTSET_HELPER_PROMPT_PARAM_IS_QUERY_SUPPORTED_KW = "wirdFrageBeantwortet"
TESTSET_HELPER_PROMPT_PARAM_ALTERNATIVE_QUERIES_KW = "passendereFrage"

TESTSET_HELPER_IS_ANSWER_FACTUALLY_HALLUCINATED_KW = "isAnswerFactuallyHallucinated"
TESTSET_HELPER_ANSWER_FACTUALLY_WRONG_MESSAGES_KW = "answerFactuallyWrongMessages"
TESTSET_HELPER_IS_ANSWER_STRUCTURALLY_HALLUCINATED_KW = "isAnswerStructurallyHallucinated"
TESTSET_HELPER_ANSWER_STRUCTURALLY_HALLUCINATED_MESSAGES_KW = "answerStructurallyHallucinatedMessages"
TESTSET_HELPER_IS_ANSWER_SEMANTICALLY_HALLUCINATED_KW = "isAnswerSemanticallyHallucinated"
TESTSET_HELPER_ANSWER_SEMANTICALLY_HALLUCINATED_MESSAGES_KW = "answerSemanticallyHallucinatedMessages"
TESTSET_HELPER_IS_ANSWER_REASONING_HALLUCINATED_KW = "isAnswerReasoningHallucinated"
TESTSET_HELPER_ANSWER_REASONING_HALLUCINATED_MESSAGES_KW = "answerReasoningHallucinatedMessages"
TESTSET_HELPER_IS_ANSWER_CITATIONWISE_HALLUCINATED_KW = "isAnswerCitationwiseHallucinated"
TESTSET_HELPER_ANSWER_CITATIONWISE_HALLUCINATED_MESSAGES_KW = "answerCitationwiseHallucinatedMessages"
TESTSET_HELPER_IS_ANSWER_CONTEXTUALLY_HALLUCINATED_KW = "isAnswerContextuallyHallucinated"
TESTSET_HELPER_ANSWER_CONTEXTUALLY_HALLUCINATED_MESSAGES_KW = "answerContextuallyHallucinatedMessages"
TESTSET_HELPER_IS_ANSWER_EXTRACTIONWISE_HALLUCINATED_KW = "isAnswerExtractionwiseHallucinated"
TESTSET_HELPER_ANSWER_EXTRACTIONWISE_HALLUCINATED_MESSAGES_KW = "answerExtractionwiseHallucinatedMessages"
TESTSET_HELPER_ALTERNATIVE_ANSWERS_KW = "alternativeAnswers"
TESTSET_HELPER_SOURCES_KW = "sources"

BENCHMARKING_EMBEDDINGS_DB = "./benchmarking/db"

# Optimizations constants
QA_DATA_PATH = "./optimizations/qa/qa_data"

# Other constants
RETRIEVAL_MODEL, GENERATION_MODEL = "llama3", "llama3"

# Usecases
"""
# muss in readme rein
UC_MELDEBESCHEINIGUNG = "meldebescheinigung"
UC_WOHNSITZ_UMZUG = "wohnsitz_umzug"
UC_GEWERBE = "gewerbe"
UC_PERSONALAUSWEIS = "personalausweis"
UC_KFZ = "kfz"
"""