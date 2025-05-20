"""Dieses Script enthält für die Anwendung wichtige Konstanten"""

DB_PATH = "./rag_pipeline/db"
OPTIMIZED_DB_PATH = "./optimizations/qa/db"
BM25_INDEX_PATH = "./optimizations/hybrid_search/bm25_index"

DATA_PATH = "./scraping/dataset/"
SCRAPED_URLS_FILE = './scraping/urls_to_scrape.json'
SCRAPED_BROKEN_LINKS_FILE = './scraping/broken_links.json'

TESTSET_PATH = "./benchmarking/testset"
USECASES_PERSONAS_PATH = "./benchmarking/use_case_personas.json"
TESTSET_SIZE_PER_USECASE = 50
TESTSET_MODEL = "llama3:70b"

QA_DATA_PATH = "./optimizations/qa/qa_data"

RETRIEVAL_MODEL, GENERATION_MODEL = "llama3", "llama3"