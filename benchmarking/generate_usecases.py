"""Dieses Script gruppiert die vorhandenen Dokumente in die angegebenen Use-Cases"""


import glob
import os
import json


FILES_DIR = '../scraping/all_files'

USECASE_KEYWORDS = {
    "meldebescheinigung": ["meldebescheinigung", "anmeldung", "abmeldung", "ummeldung"],
    "wohnsitz_umzug": ["wohnsitz", "umzug", "adresse", "anmelden", "ummelden"],
    "gewerbe": ["gewerbe", "kleingewerbe", "firma", "unternehmen"],
    "personalausweis": ["personalausweis", "ausweis", "identitätsnachweis"],
    "kfz": ["kfz", "zulassung", "auto", "fahrzeug", "kennzeichen"],
}
USECASE_SONSTIGES_KEYWORD = "sonstiges"

"""Lädt die Dokumente in den Programmspeicher"""
def load_documents():
    docs = []
    for file in glob.glob(os.path.join(FILES_DIR, "*.md")) + glob.glob(os.path.join(FILES_DIR, "*.txt")):
        with open(file, encoding="utf-8") as f:
            content = f.read()
            docs.append({"filename": os.path.basename(file), "content": content})
    return docs

"""Klassifiziert Dokument nach Use-Case"""
def assign_usecase_by_content_and_title(doc, usecase_keywords):
    content = doc["content"].lower()
    title = doc["filename"].lower()

    for usecase, keywords in usecase_keywords.items():
        if any(keyword in content for keyword in keywords) or any(keyword in title for keyword in keywords):
            return usecase
        
    return USECASE_SONSTIGES_KEYWORD

"""Gruppiert alle Dokumente nach Use-Cases"""
def group_documents_by_usecase(docs):
    docs_by_usecase = {key: [] for key in USECASE_KEYWORDS.keys()}
    docs_by_usecase[USECASE_SONSTIGES_KEYWORD] = []

    for doc in docs:
        usecase = assign_usecase_by_content_and_title(doc, USECASE_KEYWORDS)
        docs_by_usecase[usecase].append(doc["filename"])
    
    return docs_by_usecase

"""
    - Lädt alle Dokumente des Datensatzes und
    - gruppiert sie nach 5 Use-Cases
"""
def main():
    docs = load_documents()
    output_dict = group_documents_by_usecase(docs)
    with open("use_cases.json", 'w', encoding="utf-8") as f:
        json.dump(output_dict, f)
    
    print("Dokumente wurden erfolgreich nach usecases gruppiert!")


if __name__ == "__main__":
    main()