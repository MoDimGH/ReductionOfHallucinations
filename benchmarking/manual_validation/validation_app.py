import streamlit as st

from benchmarking.manual_validation.utils import get_status_color
from benchmarking.manual_validation.datahandler import DataHandler
from benchmarking.manual_validation.llm_validation_helper import check_for_incorrect, check_for_unsupported


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
        st.session_state.testset_item = len(DataHandler.testdata[st.session_state.testset]) - 1
    st.rerun()


def handle_forward_button():
    if st.session_state.testset_item < len(DataHandler.testdata[st.session_state.testset]) - 1:
        st.session_state.testset_item += 1
    elif st.session_state.testset < len(DataHandler.testdata) - 1:
        st.session_state.testset += 1
        st.session_state.testset_item = len(DataHandler.testdata[st.session_state.testset]) - 1
    st.rerun()


def main():
    # init
    DataHandler.init()
    init_session_state()

    st.set_page_config(layout="wide")
    st.title("RAGAS Testset Validator")

    testset_i = st.session_state.testset
    item_i = st.session_state.testset_item
    usecase = DataHandler.get_testset_usecase(testset_i)
    original_item = DataHandler.get_original_testset_item(usecase, item_i)

    DataHandler.init_validated_testset_item(usecase, item_i)
    DataHandler.init_helper_data_item(usecase, item_i)

    # header
    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.markdown(f"### { testset_i }. Testset ({ usecase }) - Item { item_i + 1 }/{ len(raw_original_testset) }")
    with hcol2:
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("Re-Generate", key="regenerate"):
                pass
        with btn_col2:
            if st.button("Zurück", key="back", disabled=(item_i == testset_i == 0)):
                handle_back_button()
        with btn_col3:
            if st.button("Weiter", key="forward", disabled=(item_i == len(raw_original_testset)-1 and testset_i == DataHandler.get_testset_size()-1)):
                handle_forward_button()

    st.markdown(f"**❓ Frage:** { validated_item.query or original_item.query }")
    st.markdown(f"- ")

    st.markdown(f"**✅ Generierte Antwort:** { validated_item.expected_answer or original_item.expected_answer }")
    st.markdown(f"**ℹ️ Referenz{'en' if len(validated_item.expected_contexts or original_item.expected_contexts) > 1 else ''}**")



if __name__ == "__main__":
    main()