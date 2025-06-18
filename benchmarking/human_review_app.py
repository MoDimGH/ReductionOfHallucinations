import streamlit as st

# Beispiel-Datensatz
data = [
    {
        "halluzinations_art": "Intrinsic",
        "generierte_query": "Der Betreiber eines genehmigten Reit- und Fahrbetriebs möchte künftig zusätzlich Lamas für geführte Trekking-Touren einsetzen. Erläutern Sie anhand der Rechtsgrundlage, ob die bereits nach § 11 Abs. 1 Nr. 8c TierSchG erteilte Erlaubnis automatisch auch die Haltung und Nutzung von Lamas umfasst, und begründen Sie Ihre Antwort.",
        "provokations_erläuterung": "Ein schwächeres Modell könnte fälschlich behaupten, die bestehende Genehmigung gelte generell für \"Tierhaltung\" und somit auch für Lamas – entgegen dem Kontext.",
        "generierte_ground_truth_antwort": "Nein. Die Erlaubnis bezieht sich ausdrücklich nur auf die im Antrag angegebene Tiergattung (hier Pferde) und deren Höchstzahl sowie auf die genannten Räume und Einrichtungen. Für Lamas wäre daher eine gesonderte (oder erweiterte) Erlaubnis nach § 11 Abs. 1 Nr. 8c TierSchG zu beantragen.",
        "abgerufene_quellen": ["lorem ipsum grosser absatz....", "lorem ipsum grosser absatz 2", "..."]
    },
    # Weitere Datensätze hier
]

hallucination_types = {
    "Intrinsic": "Die Antwort widerspricht explizit dem gegebenen Kontext.",
    "Extrinsic": "Die Antwort enthält plausible Informationen, die aber nicht im Kontext vorkommen.",
    "Factuality": "Die Antwort enthält objektiv falsche Fakten, unabhängig vom Kontext.",
    "Faithfulness": "Die Antwort stimmt inhaltlich nicht mit der gestellten Frage oder Aufgabe überein (z. B. falsche Form oder Ziel verfehlt).",
    "Factual Mirage": "Die Antwort klingt glaubwürdig, ist aber inhaltlich erfunden oder falsch (z. B. „Konan Doyle war Royal Detective“).",
    "Silver Lining": "Die Eingabe enthält bereits einen Fehler, und die Antwort verstärkt oder ergänzt diesen mit zusätzlichen Halluzinationen.",
    "Keine Halluzination": "Die Antwort stimmt mit dem Kontext und der Frage überein und ist korrekt."
}


# Initialisierung der Streamlit-App
st.title("Halluzinations-Datenbearbeitung")

# Aktuellen Index des Datensatzes speichern
if "index" not in st.session_state:
    st.session_state.index = 0

# Navigation zwischen den Items
def navigate(direction):
    if direction == "next":
        if st.session_state.index < len(data) - 1:
            st.session_state.index += 1
    elif direction == "prev":
        if st.session_state.index > 0:
            st.session_state.index -= 1

# Aktuelles Datensatz-Item
current_item = data[st.session_state.index]

# Anzeige der aktuellen Informationen
st.header(f"Datensatz {st.session_state.index + 1} von {len(data)}")

st.subheader("Halluzinationsart")
st.text_input("Halluzinationsart", current_item["halluzinations_art"], key="halluzinations_art")

st.subheader("Generierte Query")
st.text_area("Generierte Query", current_item["generierte_query"], key="generierte_query")

st.subheader("Provokationsbegründung")
st.text_area("Provokationsbegründung", current_item["provokations_erläuterung"], key="provokations_erläuterung")

st.subheader("Generierte Ground Truth Antwort")
st.text_area("Generierte Ground Truth Antwort", current_item["generierte_ground_truth_antwort"], key="generierte_ground_truth_antwort")

st.subheader("Abgerufene Quellen")
for i, source in enumerate(current_item["abgerufene_quellen"]):
    st.text_input(f"Quelle {i+1}", source, key=f"source_{i}")

# Navigation Buttons
col1, col2 = st.columns(2)
with col1:
    if st.session_state.index > 0:
        if st.button("Vorheriges Item"):
            navigate("prev")
with col2:
    if st.session_state.index < len(data) - 1:
        if st.button("Nächstes Item"):
            navigate("next")
