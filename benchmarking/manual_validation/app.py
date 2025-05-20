import os
import json

import streamlit as st

from rag_pipeline.constants import TESTSET_PATH, DB_PATH
from rag_pipeline.model import Model
from rag_pipeline.query_rag import generate_answer, format_sources
from rag_pipeline.utilities import create_chroma_retriever



def load_files():
    testset_dir = TESTSET_PATH
    files = [f for f in os.listdir(testset_dir) if f.endswith(".json")]
    
    data = []
    for file in files:
        with open(os.path.join(testset_dir, file), "r", encoding="utf-8") as f:
            data.extend(json.load(f))
    
    return data


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

    validation_results = generate_answer(validation_prompt)
    
    return validation_results



def main():
    st.set_page_config(layout="wide")
    st.title("RAGAS Testset Validator")

    data = load_files()

    for idx, item in enumerate(data):
        st.markdown(f"### Test {idx + 1}")
        st.markdown(f"**❓ Frage:** {item['user_input']}")
        st.markdown(f"**✅ Erwartete Antwort:** {item['reference']}")
        
        with st.expander("Referenzkontexte anzeigen"):
            for ctx in item['reference_contexts']:
                st.text_area("Kontext", value=ctx, height=150, key=f"{idx}_ctx_{ctx[:30]}")

        if st.button("🔍 Live-RAG ausführen", key=f"run_{idx}"):
            raw_result = validate_rag_pipeline(item['reference'])
            print(raw_result[raw_result.find('{') : raw_result.find('}')])
            result = json.loads(raw_result[raw_result.find('{') : raw_result.find('}')+1])
            color = "🟩" if result["status"] == "correct" else ("🟧" if result["status"] == "unsupported" else "🟥")

            st.markdown(f"{color} *{result['status']}*")
            st.markdown(f"**Generierte Antwort:** {result['report']}")
            st.markdown("**Zitate aus Quellen:**")
            for zitat in result['zitate']:
                st.code(zitat, language="text")


if __name__ == "__main__":
    Model.init()
    main()


# 1. generierung durch eine sehr gute KI
# 2. Status prüfung in 3 schritte aufteilen
# 3. wenn das nicht reicht, erst ohne json, dann einen prompt um alles in json einzufügen
# 4. wenn das nicht reicht, noch einen prompt um json zu überprüfen
# 5. komplette retrys bei fehlern
# 6. sources mit angeben
# 7. immer nur eine frage anzeigen und dann zur nächsten gehen
# 8. korrekte antwort laden / angeben und speichern