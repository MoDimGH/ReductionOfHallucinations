# TODO: neue db erstellen mit allen dateien + qa für jede seite
# TODO: cli parameter profile erstellen für rag-pipeline (standard-profil, generate-qa überschreibt datenbankzugriff)

import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from rag_pipeline.model import Model
from langchain_chroma import Chroma
from math import ceil
from langchain.prompts import ChatPromptTemplate


from rag_pipeline.model import Model
from rag_pipeline.populate_database import load_documents, split_documents, add_to_db


ORIGINAL_DB_PATH = "./rag_pipeline/db"
OPTIMIZED_DB_PATH = "./optimizations/qa_pairs/db"
DATASET_PATH = "./scraping/all_files"


QA_PROMPT_TEMPLATE = """
Given the following document page, generate 15 factual question-answer pairs that can be directly answered from the text.

Page:
{context}

Q&A pairs:
"""


# 1. load all documents
# 2. copy or create database
# 3. create all qa pairs for each page
# 3. add all qa chunks to database aswell


def main():
    documents = load_documents(DATASET_PATH)

    if os.path.exists(OPTIMIZED_DB_PATH):
        shutil.rmtree(OPTIMIZED_DB_PATH)

    if os.path.exists(ORIGINAL_DB_PATH):
        shutil.copytree(ORIGINAL_DB_PATH, OPTIMIZED_DB_PATH)
    else:
        Model.init()
        chunks = split_documents(documents)
        add_to_db(chunks, OPTIMIZED_DB_PATH)
    
    qa_documents = []
    for document in documents:
        prompt_template = ChatPromptTemplate.from_template(QA_PROMPT_TEMPLATE)
        prompt_template.format(context=document.metadata)
    







# add this to db with own id