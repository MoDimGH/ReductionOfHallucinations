import os
from rag_pipeline.constants import DATA_PATH


def get_usecase_dataset_share(target_usecase, include_pdfs=False):
    usecase_sizes = {}
    
    for usecase in os.listdir(DATA_PATH):
        usecase_path = os.path.join(DATA_PATH, usecase)
        size = 0
        for filename in os.listdir(usecase_path):
            if filename[-3:] == ".md" or include_pdfs and filename[-4:] == ".pdf":
                filepath = os.path.join(usecase_path, filename)
                size += os.path.getsize(filepath)
        
        usecase_sizes[usecase] = size
    
    total_size = sum(usecase_sizes.values())
    
    if target_usecase not in usecase_sizes:
        raise Exception(f"Usecase {target_usecase} not found")

    target_usecase_size = usecase_sizes[target_usecase]
    fraction = (target_usecase_size / total_size) if total_size > 0 else 0

    return fraction


if __name__ == "__main__":
    import json

    with open("./benchmarking/use_case_personas.json") as f:
        u = json.load(f)
    for usecase in u:
        print(get_usecase_dataset_share(usecase))
    print(sum([get_usecase_dataset_share(c) for c in u]))
