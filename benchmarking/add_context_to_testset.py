import json
import os
from tqdm import tqdm

from rag_pipeline.populate_database import clear_database, load_documents, split_documents, calculate_chunk_ids, add_to_db
from rag_pipeline.constants import DATA_PATH, USECASES_PERSONAS_PATH, TESTSET_PATH, TESTSET_DB_PATH, TESTSET_CONTEXT_KW
from benchmarking.datahandler import DataHandler

def create_db(dataset_path, db_path, embedding_model):
    print("Loading documents")
    documents = load_documents(dataset_path)
    print(f"Loaded documents successfully ({len(documents)})")

    print("Splitting documents into chunks")
    chunks = split_documents(documents)

    print("Adding chunks to database")
    chunks_with_ids = calculate_chunk_ids(chunks)

    add_to_db(chunks_with_ids, db_path=db_path, embedding_model=embedding_model)


def populate_testset_database(embedding_model):
    usecase_personas = {}
    with open(USECASES_PERSONAS_PATH) as f:
        usecase_personas = json.load(f)
    
    for usecase, _ in tqdm(usecase_personas.items()):
        dataset_path = os.path.join(DATA_PATH, usecase)
        db_path = os.path.join(TESTSET_DB_PATH, usecase)

        print(f"Populating Advanced Database")
        clear_database(db_path)
        create_db(dataset_path, db_path, embedding_model)
        print("Successfully Populated Database")

        
def add_context_to_testset():
    usecase_personas = {}
    with open(USECASES_PERSONAS_PATH) as f:
        usecase_personas = json.load(f)
    
    for usecase, _ in tqdm(usecase_personas.items()):
        testset_path = os.path.join(TESTSET_PATH, usecase + ".json")
        retriever = DataHandler.get_db(usecase).as_retriever(search_kwargs={"k": 5})

        testset = []
        with open(testset_path) as f:
            testset = json.load(f)
        
        for item in testset:
            item[TESTSET_CONTEXT_KW] = [doc.page_content for doc in retriever.invoke(item["generierte_query"])]
        
        with open(testset_path, "w") as f:
            json.dump(testset, f)
        

if __name__ == "__main__":
    DataHandler.init()
    embedding_model = DataHandler.get_embedding_model()

    populate_testset_database(embedding_model)
    DataHandler.init(reinit=True)
    add_context_to_testset()
