import glob
import os
import json


FILES_DIR = './all_files'

USECASE_KEYWORDS = {
    "meldebescheinigung": ["meldebescheinigung", "anmeldung", "abmeldung", "ummeldung"],
    "wohnsitz_umzug": ["wohnsitz", "umzug", "adresse", "anmelden", "ummelden"],
    "gewerbe": ["gewerbe", "kleingewerbe", "firma", "unternehmen"],
    "personalausweis": ["personalausweis", "ausweis", "identitätsnachweis"],
    "kfz": ["kfz", "zulassung", "auto", "fahrzeug", "kennzeichen"],
}

def load_documents():
    docs = []
    for file in glob.glob(os.path.join(FILES_DIR, "*.md")):
        with open(file, encoding="utf-8") as f:
            content = f.read()
            docs.append({"filename": os.path.basename(file), "content": content})
    return docs

def assign_usecase_by_content_and_title(doc, usecase_keywords):
    content = doc["content"].lower()
    title = doc["filename"].lower()

    for usecase, keywords in usecase_keywords.items():
        if any(keyword in content for keyword in keywords) or any(keyword in title for keyword in keywords):
            return usecase
        
    return "sonstiges"

def sort_documents_by_usecase(docs):
    docs_by_usecase = {key: [] for key in USECASE_KEYWORDS.keys()}
    docs_by_usecase["sonstiges"] = []

    for doc in docs:
        usecase = assign_usecase_by_content_and_title(doc, USECASE_KEYWORDS)
        docs_by_usecase[usecase].append(doc["filename"])
    
    return docs_by_usecase



if __name__ == "__main__":
    docs = load_documents()
    output_dict = sort_documents_by_usecase(docs)
    with open("use_cases.json", 'w', encoding="utf-8") as f:
        json.dump(output_dict, f)
    
    print("Dokumente wurden erfolgreich nach usecases gruppiert!")