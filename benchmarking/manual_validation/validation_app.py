import streamlit as st

from benchmarking.manual_validation.utils import get_status_color
from benchmarking.manual_validation.datahandler import DataHandler
from benchmarking.manual_validation.llm_validation_helper import check_query
from rag_pipeline.constants import (
    TESTSET_HELPER_PROMPT_PARAM_IS_QUERY_SUPPORTED_KW,
    TESTSET_HELPER_PROMPT_PARAM_ALTERNATIVE_QUERIES_KW
)


def init_session_state():
    if 'testset' not in st.session_state:
        st.session_state['testset'] = 0

    if 'testset_item' not in st.session_state:
        st.session_state['testset_item'] = 0


def handle_back_button():
    if st.session_state.testset_item > 0:
        st.session_state.testset_item -= 1
    elif st.session_state.testset > 0:
        st.session_state.testset -= 1
        st.session_state.testset_item = DataHandler.get_testset_size(st.session_state.testset) - 1
    st.rerun()


def handle_forward_button():
    if st.session_state.testset_item < DataHandler.get_testset_size(st.session_state.testset) - 1:
        st.session_state.testset_item += 1
    elif st.session_state.testset < DataHandler.get_testset_amount() - 1:
        st.session_state.testset += 1
        st.session_state.testset_item = 0
    st.rerun()

def generate_helper_data(usecase, item_i, original_item):
    is_query_supported_list, query_supported_message_list = [], []
    for result in check_query(original_item.query, original_item.expected_contexts):
        wirdFrageBeantwortet, erklaerung = result.get(TESTSET_HELPER_PROMPT_PARAM_IS_QUERY_SUPPORTED_KW), result.get(TESTSET_HELPER_PROMPT_PARAM_ALTERNATIVE_QUERIES_KW)
        if wirdFrageBeantwortet is None or erklaerung is None:
            continue
        is_query_supported_list.append(wirdFrageBeantwortet)
        query_supported_message_list.append(erklaerung)

    DataHandler.set_query_check(usecase, item_i, is_query_supported_list, query_supported_message_list)


def main():
    # init
    DataHandler.init()
    init_session_state()

    st.set_page_config(layout="wide")
    st.title("RAGAS Testset Validator")

    testset_i = st.session_state.testset
    item_i = st.session_state.testset_item
    usecase = DataHandler.get_testset_usecase(testset_i)
    original_item = DataHandler.get_original_testset_item(testset_i, item_i)

    DataHandler.init_validated_testset_item(usecase, item_i)
    DataHandler.init_helper_data_item(usecase, item_i)

    # header
    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.markdown(f"## { testset_i + 1 }. Testset ({ usecase }) - Item { item_i + 1 }/{ DataHandler.get_testset_size(testset_i) }")
    with hcol2:
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("Re-Generate", key="regenerate"):
                generate_helper_data(usecase, item_i, original_item)
                st.rerun()
        with btn_col2:
            if st.button("Zurück", key="back", disabled=(item_i == testset_i == 0)):
                handle_back_button()
        with btn_col3:
            if st.button("Weiter", key="forward", disabled=(item_i == DataHandler.get_testset_size(testset_i)-1 and testset_i == DataHandler.get_testset_amount()-1)):
                handle_forward_button()

    with st.container():
        frage_title = "❓ Frage:"
        frage_text = original_item.query
        draw_div(frage_title, frage_text)
        
    is_query_supported_list, alternative_queries = DataHandler.get_query_check(usecase, item_i)
    print("after_datahandler: ", is_query_supported_list)
    print("after_datahandler_frage", alternative_queries)
    if is_query_supported_list:
        with st.expander(label="Alternative Fragen"):
            for is_query_supported, alternative_query in zip(is_query_supported_list, alternative_queries):
                st.markdown(f"- { get_status_color(is_query_supported) } { alternative_query }")

    with st.container():
        expected_answer_title = "✅ Generierte Antwort:"
        expected_answer_text = original_item.expected_answer
        draw_div(expected_answer_title, expected_answer_text)

    with st.container():
        references_title = f"ℹ️ Referenz{'en' if len( original_item.expected_contexts) > 1 else ''}"
        references_text = "".join([f"""<div style="border:{"1px solid lightgray"}; padding:10px; margin:10px;  border-radius:10px;">
                    { context }
                </div>""" for context in original_item.expected_contexts])

        draw_div(references_title, references_text, custom_html=True)


def draw_div(title, text, custom_html=False):
    st.markdown(get_div_html(title, text, custom_html), unsafe_allow_html=True)

def get_div_html(title, text, custom_html=False):
    return (f"""
        <div style="border:{"1px solid lightgray"}; padding:10px; margin:10px;  border-radius:10px;">
            {title and f"<h3>{ title }</h3>"}
            {text if custom_html else f"<p style='white-space: pre-wrap'>{ text }</p>"}
        </div>
    """)


if __name__ == "__main__":
    main()