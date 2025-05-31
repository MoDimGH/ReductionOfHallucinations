import os
import json
import streamlit as st

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

from rag_pipeline.constants import TESTSET_PATH, DB_PATH, TESTSET_GENERATION_MODEL, TESTSET_EMBEDDING_MODEL, TESTSET_DB_PATH, TESTSET_VALIDATION_REFERENCES_KW, TESTSET_VALIDATION_EXPECTED_ANSWER_KW, TESTSET_VALIDATED_DATA_PATH
from rag_pipeline.model import Model
from rag_pipeline.query_rag import generate_answer, format_sources
from rag_pipeline.populate_database import load_db
from rag_pipeline.utilities import create_chroma_retriever


class DataHandler:
    dbs = []
    model = None
    testdata = []


    @classmethod
    def init(cls):
        if not cls.dbs:
            embedding_model = OllamaEmbeddings(model=TESTSET_EMBEDDING_MODEL)
            for db_path in os.listdir(TESTSET_DB_PATH):
                cls.dbs.append(load_db(db_path, embedding_model))
        if not cls.model:
            cls.model = ChatOllama(model=TESTSET_GENERATION_MODEL)
        if not cls.testdata:
            cls.testdata = list(load_testdata().items())


def load_testdata():
    testset_dir = TESTSET_PATH
    filepaths = [f for f in os.listdir(testset_dir) if f.endswith(".json")]
    
    data = {}
    for filepath in filepaths:
        with open(os.path.join(testset_dir, filepath), "r", encoding="utf-8") as f:
            data[os.path.basename(filepath)] = json.load(f)

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


def load_validated_data():
    with open(TESTSET_VALIDATED_DATA_PATH) as f:
        return json.load(f)

def save_validated_data(data):
    with open(TESTSET_VALIDATED_DATA_PATH, 'w') as f:
        json.dump(data, f)


def get_validated_data(usecase, ix):
    data = load_validated_data()
    return data.get(usecase).get(str(ix))


def save_validated_expected_answer(usecase, i, validated_answer):
    data = load_validated_data()
    data[usecase][str(i)][TESTSET_VALIDATION_EXPECTED_ANSWER_KW] = validated_answer
    save_validated_data(data)
    

def save_validated_references(usecase, ix, validated_ids):
    data = load_validated_data()
    data[usecase][str(ix)][TESTSET_VALIDATION_REFERENCES_KW] = validated_ids
    save_validated_data(data)


def get_status_color(status):
    return "🟩" if status == 2 else "🟥" if status == 1 else "🟧"


def main():
    DataHandler.init()
    if 'testset_ix' not in st.session_state:
        st.session_state['testset_ix'] = 0
    
    if 'testelement_ix' not in st.session_state:
        st.session_state['testelement_ix'] = 0

    st.set_page_config(layout="wide")
    st.title("RAGAS Testset Validator")

    i = st.session_state.testelement_ix
    
    current_usecase, current_testdata = DataHandler.testdata[st.session_state.testset_ix]
    current_testcase = current_testdata[i]
    query = current_testcase['user_input']
    expected_contexts = current_testcase['reference_contexts']
    expected_answer = current_testcase['reference']

    if st.button("Zurück", key="back"):
        if st.session_state.testelement_ix > 0:
            st.session_state.testelement_ix -= 1
        elif st.session_state.testset_ix > 0:
            st.session_state.testset_ix -= 1
            st.session_state.testelement_ix = len(DataHandler.testdata[st.session_state.testset_ix]) - 1
        st.rerun()

    if st.button("Weiter", key="forward"):
        if st.session_state.testelement_ix < len(DataHandler.testdata[st.session_state.testset_ix]) - 1:
            st.session_state.testsetelement_ix += 1
        elif st.session_state.testset_ix < len(DataHandler.testdata) - 1:
            st.session_state.testset_ix += 1
            st.session_state.testelement_ix = len(DataHandler.testdata[st.session_state.testset_ix]) - 1
        st.rerun()

    st.markdown(f"### Testset { st.session_state.testset_ix }: Test { i + 1 }")
    st.markdown(f"**❓ Frage:** { query }")
    st.markdown(f"**✅ Erwartete Antwort:** { expected_answer }")

    validated_answer = st.text_input(value=get_validated_data(current_usecase, i), label="Valid Answer")
    save_validated_expected_answer(current_usecase, i, validated_answer)

    if "selected_ids" not in st.session_state:
        st.session_state.selected_ids = get_validated_data(current_usecase, i)[TESTSET_VALIDATION_REFERENCES_KW]

    if st.button("🔍 Live-RAG ausführen", key=f"run_{i}"):
        status, quellen = validate_testcase(expected_answer)
        st.markdown(f"*Incorrect-Check:* {get_status_color(status['incorrect'])}")
        st.markdown(f"*Unsupported-Check:* {get_status_color(status['unsupported'])}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Referenzkontexte")
            for idx, ctx in enumerate(expected_contexts):
                ctx_id = f"ref_{idx}"
                confidence = 0.95  # Platzhalterwert
                is_selected = ctx_id in st.session_state.selected_ids
                border_color = "3px solid green" if is_selected else "1px solid lightgray"

                with st.container():
                    if st.button(f"{'☑️' if is_selected else '⬜'} {ctx_id}", key=f"sel_{ctx_id}"):
                        if is_selected:
                            st.session_state.selected_ids.remove(ctx_id)
                        elif len(st.session_state.selected_ids) < 5:
                            st.session_state.selected_ids.append(ctx_id)
                        save_validated_references(current_usecase, i, st.session_state.selected_ids)
                        st.rerun()

                    st.markdown(f"""
                        <div style="border:{border_color}; padding:10px; border-radius:10px;">
                            <b>Confidence:</b> {confidence}<br>
                            <p style='white-space: pre-wrap'>{ctx}</p>
                        </div>
                    """, unsafe_allow_html=True)

        with col2:
            st.markdown("### RAG-Quellen")
            for idx, quelle in enumerate(quellen):
                q_id = f"rag_{idx}"
                confidence = 0.87  # Platzhalterwert
                is_selected = q_id in st.session_state.selected_ids
                border_color = "3px solid green" if is_selected else "1px solid lightgray"

                with st.container():
                    if st.button(f"{'☑️' if is_selected else '⬜'} {q_id}", key=f"sel_{q_id}"):
                        if is_selected:
                            st.session_state.selected_ids.remove(q_id)
                        elif len(st.session_state.selected_ids) < 5:
                            st.session_state.selected_ids.append(q_id)
                        save_validated_references(current_usecase, i, st.session_state.selected_ids)
                        st.rerun()

                    st.markdown(f"""
                        <div style="border:{border_color}; padding:10px; border-radius:10px;">
                            <b>Confidence:</b> {confidence}<br>
                            <p style='white-space: pre-wrap'>{quelle}</p>
                        </div>
                    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()


# 1. generierung durch eine sehr gute KI
# 2. Status prüfung in 3 schritte aufteilen
# 3. wenn das nicht reicht, erst ohne json, dann einen prompt um alles in json einzufügen
# 4. wenn das nicht reicht, noch einen prompt um json zu überprüfen
# 5. komplette retrys bei fehlern
# 6. sources mit angeben
# 7. immer nur eine frage anzeigen und dann zur nächsten gehen
# 8. korrekte antwort laden / angeben und speichern