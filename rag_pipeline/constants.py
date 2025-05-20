"""Dieses Script enthält für die Anwendung wichtige Konstanten"""

DB_PATH = "./rag_pipeline/db"
OPTIMIZED_DB_PATH = "./optimizations/qa/db"
BM25_INDEX_PATH = "./optimizations/hybrid_search/bm25_index"

DATA_PATH = "./scraping/all_files/"
SCRAPED_URLS_FILE = './scraping/urls_to_scrape.json'
SCRAPED_BROKEN_LINKS_FILE = './scraping/broken_links.json'
TESTSET_PATH = "./benchmarking/testsets"
QA_DATA_PATH = "./optimizations/qa/qa_data"

RETRIEVAL_MODEL, GENERATION_MODEL = "llama3", "llama3"