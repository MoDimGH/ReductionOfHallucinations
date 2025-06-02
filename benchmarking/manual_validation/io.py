import os
import json

from rag_pipeline.constants import (
    TESTSET_PATH,
    TESTSET_VALIDATED_PATH, 
    TESTSET_TEST_ITEM_TEMPLATE_PATH, 
    TESTSET_HELPER_DATA,
    TESTSET_HELPER_DATA_ITEM_TEMPLATE,
    TESTSET_HELPER_GENERATED_ANSWER_KW, 
    TESTSET_HELPER_REFERENCES_KW
)


def load_original_testsets() -> dict[str, list]:
    filepaths = [f for f in os.listdir(TESTSET_PATH) if f.endswith(".json")]
    data = {}
    for filepath in filepaths:
        with open(os.path.join(TESTSET_PATH, filepath), "r", encoding="utf-8") as f:
            data[os.path.basename(filepath).rstrip(".json")] = json.load(f)

    return data

def load_validated_testsets() -> dict[str, list]:
        with open(TESTSET_VALIDATED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def save_validated_testsets(data):
    with open(TESTSET_VALIDATED_PATH, 'w') as f:
        json.dump(data, f)

def load_testset_item_template():
    with open(TESTSET_TEST_ITEM_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_helper_data():
    with open(TESTSET_HELPER_DATA, "r", encoding="utf-8") as f:
        return json.load(f)

def save_helper_data(data):
    with open(TESTSET_HELPER_DATA, 'w') as f:
        json.dump(data, f)

def load_helper_data_item_template():
    with open(TESTSET_HELPER_DATA_ITEM_TEMPLATE, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------


def init_helper_data_item(usecase, i):
    data = load_helper_data()
    if usecase not in data:
        raise Exception("Invalid Usecase.")
    
    if not data.get(usecase).get(str(i)):
        data[usecase][str(i)] = { TESTSET_HELPER_GENERATED_ANSWER_KW: "", TESTSET_HELPER_REFERENCES_KW: [] }
    
    save_helper_data(data)


def get_helper_data_item(usecase, i):
    data = load_helper_data()
    return data.get(usecase).get(str(i))


def save_helper_expected_answer(usecase, i, helper_answer):
    data = load_helper_data()
    data[usecase][str(i)][TESTSET_HELPER_GENERATED_ANSWER_KW] = helper_answer
    save_helper_data(data)
    

def save_helper_references(usecase, i, helper_references):
    data = load_helper_data()

    data[usecase][str(i)][TESTSET_VALIDATION_REFERENCES_KW] = helper_references
    save_helper_data(data)
