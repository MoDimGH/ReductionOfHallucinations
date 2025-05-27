import os
import json

import streamlit as st

from rag_pipeline.constants import TESTSET_PATH, DB_PATH
from rag_pipeline.model import Model
from rag_pipeline.query_rag import generate_answer, format_sources
from rag_pipeline.populate_database import load_db
from rag_pipeline.utilities import create_chroma_retriever
from langchain_ollama import ChatOllama


class DataHandler:
    db = None
    model = None
    testdata = None

    @classmethod
    def init(cls):
        if not cls.db:
            cls.db = load_db(DB_PATH, Model.getEmbeddingFunction())
        if not cls.model:
            cls.model = ChatOllama(model="mistral-nemo")
        if not cls.testdata:
            cls.testdata = load_files()


def load_files():
        testset_dir = TESTSET_PATH
        files = [f for f in os.listdir(testset_dir) if f.endswith(".json")]
        
        data = []
        for file in files:
            with open(os.path.join(testset_dir, file), "r", encoding="utf-8") as f:
                data.extend(json.load(f))
    
        return data


def query(query):
    # return generate_answer(validation_prompt)
    return DataHandler.model.invoke(query)


def validate_rag_pipeline(expected_answer):
    retriever = create_chroma_retriever(DB_PATH)
    sources = format_sources(retriever.invoke(expected_answer))

    validation_prompt = f"""Hier ist die Antwort, die du mir vorhin gegeben hast: {expected_answer}

        -------------------------------------------------

        Bitte prüfe die Quellen in der folgenden json-Liste. 

        Quellen: {sources}
        
        -------------------------------------------------

        Wenn alle Teile der Antwort durch die Quellen gestützt werden, dann gib mir bitte die genauen Zitate aus den Quellen an, die die Antwort unterstützen. In diesem Fall melde bitte den Status "correct". 
        Wenn ein Teil der Antwort nicht durch die Quellen gestützt wird, gib mir bitte die genauen Zitate aus der Antwort an, die nicht gestützt wird. In diesem Fall melde bitte den Status "unsupported".
        Wenn ein Teil der Antwort falsch ist und im Widerspruch zu den Informationen in den Quellen steht, dann gib mir bitte die genauen Zitate aus den Quellen an, die im Widerspruch zur Antwort stehen. In diesem Fall melde bitte den Status "incorrect".

        Deine Evalutierungsantwort gebe bitte unter "report" an.
        
        Bitte antworte strikt nach dem json-Format aus dem folgenden Beispiel. Bitte Antwort nichts anderes als das json:

        {{
            "report": "Teile der Antwort werden nicht von den Quellen unterstützt. Hamburg ist nicht die Hautstadt von Deutschand. Auch ist für einen Personalausweisantrag eine Gebühr zu zahlen."
            "status": "incorrect",
            "zitate": ["in Hamburg, der Hauptstadt von Deutschland", "für einen Personalausweisantrag müssen Sie keine Gebühr zahlen"]
        }}
    """

    validation_results = query(validation_prompt)
    
    return validation_results


def check_for_incorrect(expected_answer, sources):
    validation_prompt = f"""
        Bitte gleiche folgende Aussage mit den folgenden Quellen ab:
        
        Aussage: { expected_answer }

        Quellen: { sources }

        =>

        Wenn die Aussage ganz mit den Informationen aus den Quellen übereinstimmt, sage einfach "wahr". Ansonsten sage einfach "falsch".
    """
    validation_result = ""
    for _ in range(5):
        validation_result = query(validation_prompt)
        if validation_result in ["wahr", "falsch"]:
            break
    print(validation_result)

    return 1 if validation_result == "falsch" else 2 if validation_result == "wahr" else 0


def check_for_unsupported(expected_answer, sources):
    validation_prompt = f"""
        Bitte gleiche folgende Aussage mit den folgenden Quellen ab:
        
        Aussage: { expected_answer }

        Quellen: { sources }

        =>

        Wenn die Informationenen der Aussage nicht in den Quellen nicht wiedergefunden werden können, sage einfach "fehlt". Ansonsten sage einfach "gefunden".
    """

    validation_result = ""
    for _ in range(5):
        validation_result = query(validation_prompt)
        if validation_result in ["gefunden", "fehlt"]:
            break
    print(validation_result)
    return 1 if validation_result == "fehlt" else 2 if validation_result == "gefunden" else 0


def validate_testcase(expected_answer):
    raw_sources = DataHandler.db.similarity_search_with_relevance_scores(expected_answer, k=5)
    # sources = [s.get("excerpt") for s in format_sources(raw_sources)]
    sources = [(doc, doc.metadata.get("id", None), _score) for doc, _score in raw_sources]
    sources.sort(key=lambda x: x[2], reverse=True)
    source_contents = [s[0] for s in sources]

    incorrect_validation_result = check_for_incorrect(expected_answer, source_contents)
    
    unsupported_validation_result = check_for_unsupported(expected_answer, source_contents)
    
    return {"incorrect": incorrect_validation_result, "unsupported": unsupported_validation_result}, sources


def load_validated_answers():
    with open("./benchmarking/manual_validation/validated_answers.json") as f:
        return json.load(f)

def load_validated_answer(i):
    answers = load_validated_answers()
    return answers.get(str(i))

def save_validated_answer(i, validated_answer):
    answers = load_validated_answers()
    answers[str(i)] = validated_answer
    
    with open("./benchmarking/manual_validation/validated_answers.json", 'w') as f:
        json.dump(answers, f)


def get_status_color(status):
    return "🟩" if status == 2 else "🟥" if status == 1 else "🟧"


def main():
    st.set_page_config(layout="wide")
    st.title("RAGAS Testset Validator")

    i = st.session_state.current_i
    item = DataHandler.testdata[i]
    query = item['user_input']
    expected_contexts = item['reference_contexts']
    expected_answer = item['reference']

    if st.session_state.current_i > 0 and st.button("Zurück", key="back"):
        st.session_state.current_i -= 1
        st.rerun()
    
    if st.session_state.current_i < len(DataHandler.testdata) - 1 and st.button("Weiter", key="forward"):
        st.session_state.current_i += 1
        st.rerun()

    st.markdown(f"### Test {i + 1}")
    st.markdown(f"**❓ Frage:** { query }")
    st.markdown(f"**✅ Erwartete Antwort:** { expected_answer }")
    
    with st.expander("Referenzkontexte anzeigen"):
        for ctx in expected_contexts:
            st.text_area("Kontext", value=ctx, height=150, key=f"{i}_ctx_{ctx[:30]}")
        
    validated_answer = st.text_input(value=load_validated_answer(i), label="Valid Answer")
    save_validated_answer(i, validated_answer)


    if st.button("🔍 Live-RAG ausführen", key=f"run_{i}"):
        status, quellen = validate_testcase(expected_answer)
        incorrect_check_color = get_status_color(status["incorrect"])
        unsupported_check_color = get_status_color(status["unsupported"])

        st.markdown(f"*Incorrect-Check:* {incorrect_check_color}")
        st.markdown(f"*Unsupported-Check:* {unsupported_check_color}")
        # st.markdown(f"**Generierte Antwort:** { report }")
        st.markdown("**Quellen:**")
        for quelle in quellen:
            st.code(quelle, language="text")


if __name__ == "__main__":
    # Model.init()
    DataHandler.init()
    if 'current_i' not in st.session_state:
        st.session_state['current_i'] = 0
    main()


# 1. generierung durch eine sehr gute KI
# 2. Status prüfung in 3 schritte aufteilen
# 3. wenn das nicht reicht, erst ohne json, dann einen prompt um alles in json einzufügen
# 4. wenn das nicht reicht, noch einen prompt um json zu überprüfen
# 5. komplette retrys bei fehlern
# 6. sources mit angeben
# 7. immer nur eine frage anzeigen und dann zur nächsten gehen
# 8. korrekte antwort laden / angeben und speichern