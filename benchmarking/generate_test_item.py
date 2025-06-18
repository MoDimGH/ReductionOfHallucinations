import json
import os
from tqdm import tqdm

from langchain_community.document_loaders import DirectoryLoader
from langchain.prompts import ChatPromptTemplate
from benchmarking.datahandler import DataHandler
from benchmarking.utilities import get_usecase_dataset_share
from rag_pipeline.constants import DATA_PATH, USECASES_PERSONAS_PATH, TESTSET_PATH, TESTSET_SIZE


def with_n_retrys(n, func):
    for _ in range(n):
        try:
            return func()
        except:
            pass
    return None


def query_model(query) -> list[str]:
    answers = []
    for i in range(1):
        answer = with_n_retrys(3, lambda: DataHandler.get_generation_model().invoke(query))
        if answer:
            answers.append(answer.content)
            
    return answers

def generate_test_items(n_queries, existing_queries, docs):
    prompt_template = ChatPromptTemplate.from_template("""
    Du bist ein Experte für RAG-Halluzinations-Evaluierung. Generiere auf Basis des Kontextes {n_queries} Queries, welche eine zufällige der folgenden Halluzinationsarten bei schwacheren Models möglichst effektiv provozieren soll. Generiere fuer die Provokation der Halluzinationen möglichst komplexe oder abstrakte Fragen wo man mehr Nachdenken und mehr Informationen miteinander verknüpfen muss:
    
    ======================================================
                                                       
    Halluzinationsarten: 
                                                       
    - **Intrinsic**: Die Antwort widerspricht explizit dem gegebenen Kontext.
    - **Extrinsic**: Die Antwort enthält plausible Informationen, die aber nicht im Kontext vorkommen.
    - **Factuality**: Die Antwort enthält objektiv falsche Fakten, unabhängig vom Kontext.
    - **Faithfulness**: Die Antwort stimmt inhaltlich nicht mit der gestellten Frage oder Aufgabe überein (z. B. falsche Form oder Ziel verfehlt).
    - **Factual Mirage**: Die Antwort klingt glaubwürdig, ist aber inhaltlich erfunden oder falsch (z. B. „Konan Doyle war Royal Detective“).
    - **Silver Lining**: Die Eingabe enthält bereits einen Fehler, und die Antwort verstärkt oder ergänzt diesen mit zusätzlichen Halluzinationen.
    - **Keine Halluzination**: Die Antwort stimmt mit dem Kontext und der Frage überein und ist korrekt.

    ======================================================

    Kontext: 

    {context}

    ======================================================
    
    Generiere neben den {n_queries} Queries ausserdem jeweils eine Ground-Truth-Antwort ausschliesslich auf Basis des Kontextes. Diese soll nachher mit der Antwort des schwacheren Models verglichen werden, in der Hoffnung, eine Halluzination zu erkennen oder auszuschliessen. Achte darauf, dass deine Queries sich deutlich von den anderen zuvor generierten Queries im Testset unterscheidet.

    ======================================================

    Bereits generierte Queries:
                                                       
    {existing_queries}
                                                       
    ======================================================

    Antworte im folgenden JSON-Format:
    [
    {{
    "halluzinations_art": "<Art>",
    "generierte_query": "<Query>",
    "provokations_erläuterung": "<Erläuterung der Halluzinations-Provokation in 1-2 Sätzen>",
    "generierte_ground_truth_antwort": "<Antwort>"
    }},
    {{  }}
    ]
    """)

    context = "\n-----------------------------------------------------------------------\n".join(docs)

    prompt = prompt_template.format(n_queries=n_queries, existing_queries=existing_queries, context=context)


    response = with_n_retrys(5, lambda: DataHandler.get_openai_client().responses.create(model="o3", input=prompt))

    text = response.output_text

    start_idx = text.find('[')
    end_idx = text.rfind(']')

    raw_json = text[start_idx:end_idx + 1]

    print(raw_json)

    return json.loads(raw_json)


def get_existing_queries(testset):
    return [item.get("generierte_query", "") for item in testset]


if __name__ == "__main__":
    MAX_DATASET_ITEMS = 5
    DataHandler.init()

    usecase_personas = {}
    with open(USECASES_PERSONAS_PATH) as f:
        usecase_personas = json.load(f)

    for usecase, persona in tqdm(usecase_personas.items()):
        if usecase != "kfz":
            continue
        md_documents = DirectoryLoader(os.path.join(DATA_PATH, usecase), recursive=True, glob="*.md").load()
        print("loaded files")

        data_batches = [[]]
        for i, doc in enumerate(md_documents):
            if (i+1) % MAX_DATASET_ITEMS == 0:
                data_batches.append([])
            data_batches[-1].append(doc.page_content)

        testset = []
        for batch in tqdm(data_batches, desc=f"Generating testset for {usecase}..."):
            n_queries = TESTSET_SIZE * get_usecase_dataset_share(usecase) / len(data_batches)
            existing_queries = get_existing_queries(testset)
            sub_testset = generate_test_items(n_queries, existing_queries, batch)
            testset.extend(sub_testset)

        with open(os.path.join(TESTSET_PATH, usecase + ".json"), "w", encoding="utf-8") as f:
            json.dump(testset, f)