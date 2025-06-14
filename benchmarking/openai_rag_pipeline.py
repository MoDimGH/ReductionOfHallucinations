

from rag_pipeline.populate_database import load_documents, split_documents, calculate_chunk_ids, add_to_db, clear_database


def load_docs(path):
    documents = load_documents(path, load_pdfs=False)
    chunks = split_documents(documents)
    return calculate_chunk_ids(chunks)

def populate_database(dataset_path, db_path, embedding_model):
    print("Load Documents...")
    docs = load_docs(dataset_path)
    print(f"{len(docs)} documents loaded")
    
    print("Create Database...")
    clear_database(db_path)
    add_to_db(docs, db_path, embedding_model=embedding_model)
    print("Database created successfully")

    return docs