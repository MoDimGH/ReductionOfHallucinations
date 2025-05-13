"""Dieses Script erstellt einen Whoosh-Index für das Sparse-Indexing"""

from tqdm import tqdm

from whoosh.index import create_in, open_dir

from whoosh.fields import Schema, TEXT

from rag_pipeline.constants import BM25_INDEX_PATH, DB_PATH
from rag_pipeline.populate_database import load_db
from rag_pipeline.model import Model


"""Lädt die Whoosh Instanz wenn vorhanden oder erstellt eine neue"""
def load_whoosh_instance(reset):
    if reset:
        print("Entferne bestehenden Whoosh Index")
        schema = Schema(
            id=TEXT(stored=True),
            page_content=TEXT(stored=True)
        )
        return create_in(BM25_INDEX_PATH, schema)
    else:
        return open_dir(BM25_INDEX_PATH)

"""Lädt alle Dokumente aus der Datenbank der RAG-Pipeline"""
def load_documents():
    Model.init()
    db = load_db(DB_PATH, Model.getEmbeddingFunction())
    db_content = db.get(include=["documents"])
    print(f"Dokumente erfolgreich geladen ({ len(db_content.get('ids')) })")
    return zip(db_content.get("ids"), db_content.get("documents"))

"""Gibt alle existierenden Ids im Whoosh Index zurück"""
def get_existing_ids(ix):
    with ix.searcher() as searcher:
        return [doc["id"] for doc in searcher.all_stored_fields()]

"""Fügt alle fehlenden Dokumente in den Whoosh Index hinzu"""
def add_documents(documents, ix):
    existing_ids = get_existing_ids(ix)
    writer = ix.writer()
    counter = 0
    for page_id, page_content in tqdm(documents):
        if page_id in existing_ids:
            continue
        writer.add_document(page_content=page_content, id=page_id)
        counter += 1
    writer.commit()

    print(f" { counter } Dokumente zum Whoosh-Index hinzugefügt ({ ix.reader().doc_count() })")

"""Erstellt einen Whoosh Index mit allen Dokumenten aus der Datenbank"""
def main(reset=False):
    print("Lade Whoosh-Index...")
    ix = load_whoosh_instance(reset)

    print("Lade Dokumente aus Datensatz...")
    documents = load_documents()

    print("Füge fehlende Dokumente zum Whoosh-Index hinzu...")
    add_documents(documents, ix)


if __name__ == "__main__":
    main()