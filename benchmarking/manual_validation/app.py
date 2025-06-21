import streamlit as st

from rag_pipeline.constants import TESTSET_VALIDATION_EXPECTED_ANSWER_KW, TESTSET_VALIDATION_REFERENCES_KW

from benchmarking.manual_validation.utils import get_status_color
from benchmarking.io import init_validated_data_item, get_validated_data_item, save_validated_expected_answer, save_validated_references
from benchmarking.datahandler import DataHandler
from benchmarking.llm_validation_helper import check_for_incorrect, check_for_unsupported


def validate_testcase(usecase, question, expected_answer):
    raw_sources = DataHandler.dbs.get(usecase).similarity_search_with_relevance_scores(question)
    # sources = [s.get("excerpt") for s in format_sources(raw_sources)]
    sources = [(doc, doc.metadata.get("id", None), _score) for doc, _score in raw_sources]
    sources.sort(key=lambda x: x[2], reverse=True)
    source_contents = [s[0] for s in sources]

    incorrect_validation_result = check_for_incorrect(expected_answer, source_contents)
    unsupported_validation_result = check_for_unsupported(expected_answer, source_contents)
    
    return {"incorrect": incorrect_validation_result, "unsupported": unsupported_validation_result}, sources


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

    init_validated_data_item(current_usecase, i)

    if st.button("Zurück", key="back"):
        if st.session_state.testelement_ix > 0:
            st.session_state.testelement_ix -= 1
        elif st.session_state.testset_ix > 0:
            st.session_state.testset_ix -= 1
            st.session_state.testelement_ix = len(DataHandler.testdata[st.session_state.testset_ix]) - 1
        st.rerun()

    if st.button("Weiter", key="forward"):
        if st.session_state.testelement_ix < len(DataHandler.testdata[st.session_state.testset_ix]) - 1:
            st.session_state.testelement_ix += 1
        elif st.session_state.testset_ix < len(DataHandler.testdata) - 1:
            st.session_state.testset_ix += 1
            st.session_state.testelement_ix = len(DataHandler.testdata[st.session_state.testset_ix]) - 1
        st.rerun()

    st.markdown(f"### Testset { st.session_state.testset_ix }: Test { i + 1 }")
    st.markdown(f"**❓ Frage:** { query }")
    st.markdown(f"**✅ Generierte Antwort:** { expected_answer }")
    st.markdown(f"**ℹ️ Referenz{'en' if len(expected_contexts) > 1 else ''}**")
    for reference in expected_contexts:
        st.write(reference)

    validated_answer = st.text_input(value=get_validated_data_item(current_usecase, i).get(TESTSET_VALIDATION_EXPECTED_ANSWER_KW), label="Valid Answer")
    save_validated_expected_answer(current_usecase, i, validated_answer)

    if "selected_ids" not in st.session_state:
        st.session_state.selected_ids = get_validated_data_item(current_usecase, i).get(TESTSET_VALIDATION_REFERENCES_KW)

    if st.button("🔍 Live-RAG ausführen", key=f"run_{i}"):
        status, quellen = validate_testcase(current_usecase, query, expected_answer)
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
            for quelle, source_id, confidence in quellen:
                is_selected = source_id in st.session_state.selected_ids
                border_color = "3px solid green" if is_selected else "1px solid lightgray"

                with st.container():
                    if st.button(f"{'☑️' if is_selected else '⬜'} {source_id}", key=f"sel_{source_id}"):
                        if is_selected:
                            st.session_state.selected_ids.remove(source_id)
                        elif len(st.session_state.selected_ids) < 5:
                            st.session_state.selected_ids.append(source_id)
                        save_validated_references(current_usecase, i, [quellen[id][1] for id in st.session_state.selected_ids])
                        st.rerun()

                    st.markdown(f"""
                        <div style="border:{border_color}; padding:10px; border-radius:10px;">
                            <b>Confidence:</b> {confidence}<br>
                            <p style='white-space: pre-wrap'>{quelle}</p>
                        </div>
                    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()


# 1. generierung durch eine sehr gute KI für fehlende und unsupported hallucinations
# 2. Status prüfung in 3 schritte aufteilen
# 3. wenn das nicht reicht, erst ohne json, dann einen prompt um alles in json einzufügen
# 4. wenn das nicht reicht, noch einen prompt um json zu überprüfen
# 5. komplette retrys bei fehlern
# 6. sources mit angeben
# 7. immer nur eine frage anzeigen und dann zur nächsten gehen
# 8. korrekte antwort laden / angeben und speichern