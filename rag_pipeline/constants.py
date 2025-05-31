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
CLEAN_DATASET = './benchmarking/clean_dataset'

# Testset constants
TESTSET_PATH = "./benchmarking/testset"
TESTSET_DB_PATH = "./benchmarking/dbs"
USECASES_PERSONAS_PATH = "./benchmarking/use_case_personas.json"
KNOWLEDGE_GRAPH_PATH = './benchmarking/knowledge_graph.json'
TESTSET_VALIDATED_DATA_PATH = './benchmarking/manual_validation/validated_data.json'
TESTSET_SIZE_PER_USECASE = 50
TESTSET_GENERATION_MODEL = "mistral-nemo"
TESTSET_EMBEDDING_MODEL = "bge-large"
TESTSET_VALIDATION_REFERENCES_KW = "references"
TESTSET_VALIDATION_EXPECTED_ANSWER_KW = "expected_answer"

# Optimizations constants
QA_DATA_PATH = "./optimizations/qa/qa_data"

# Other constants
RETRIEVAL_MODEL, GENERATION_MODEL = "llama3", "llama3"

# Usecases
"""
UC_MELDEBESCHEINIGUNG = "meldebescheinigung"
UC_WOHNSITZ_UMZUG = "wohnsitz_umzug"
UC_GEWERBE = "gewerbe"
UC_PERSONALAUSWEIS = "personalausweis"
UC_KFZ = "kfz"
"""