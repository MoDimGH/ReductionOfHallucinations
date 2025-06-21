import streamlit as st

from benchmarking.datahandler import DataHandler
from benchmarking.testset_item import TestsetItem



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
    retrieved_validated_item = DataHandler.get_validated_testset_item(usecase, item_i)
    if f'validated_item_{testset_i}_{item_i}' not in st.session_state:
        st.session_state[f'validated_item_{testset_i}_{item_i}'] = retrieved_validated_item or TestsetItem()
    validated_item = st.session_state[f'validated_item_{testset_i}_{item_i}']

    # header
    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.markdown(f"## { testset_i + 1 }. Testset ({ usecase }) - Item { item_i + 1 }/{ DataHandler.get_testset_size(testset_i) }")
    with hcol2:
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.write("✅ Validated" if retrieved_validated_item else "⏳ Pending validation"):
                st.rerun()
        with btn_col2:
            if st.button("Zurück", key="back", disabled=(item_i == testset_i == 0)):
                handle_back_button()
        with btn_col3:
            if st.button("Weiter", key="forward", disabled=(item_i == DataHandler.get_testset_size(testset_i)-1 and testset_i == DataHandler.get_testset_amount()-1)):
                handle_forward_button()

        
    st.subheader("Generierte Query")
    validated_item.generierte_query = st.text_area("Generierte Query", validated_item.generierte_query or original_item.generierte_query, key="generierte_query")

    validated_item.halluzinations_art = st.text_input("Halluzinationsart", validated_item.halluzinations_art or original_item.halluzinations_art, key="halluzinations_art")
    validated_item.provokations_erlaeuterung = st.text_area("Provokationsbegründung", validated_item.provokations_erlaeuterung or original_item.provokations_erlaeuterung, key="provokations_erläuterung")
    
    st.subheader("Generierte Ground Truth Antwort")
    validated_item.generierte_ground_truth_antwort = st.text_area("Generierte Ground Truth Antwort", validated_item.generierte_ground_truth_antwort or original_item.generierte_ground_truth_antwort, key="generierte_ground_truth_antwort")

    st.subheader("Abgerufene Quellen")
    validated_item.abgerufene_quellen = original_item.abgerufene_quellen
    for i, source in enumerate(original_item.abgerufene_quellen):
        with st.container():
            st.write(f"**Quelle {i+1}:**\n {source}")
            st.divider()

    if st.button("Validieren", key=f"validieren{testset_i}_{item_i}"):
        DataHandler.save_validated_testset_item(usecase, item_i, validated_item)
        st.rerun()

if __name__ == "__main__":
    main()