from openai import OpenAI
import pandas as pd
import time
import os

# API-Key einlesen
#openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Beispiel-Daten
df = pd.DataFrame({
    "question": [
        "Wie lange ist ein Personalausweis gültig?",
        "Wer war der erste Bundeskanzler?",
        "Was ist die Hauptstadt von Frankreich?"
    ],
    "response": [
        "Der Personalausweis ist 15 Jahre gültig.",
        "Angela Merkel war die erste Bundeskanzlerin.",
        "Paris ist die Hauptstadt von Frankreich."
    ],
    "expected_answer": [
        "10 Jahre",
        "Konrad Adenauer",
        "Paris"
    ],
    "contexts": [
        "Laut hamburg.de sind Personalausweise für Personen über 24 Jahre 10 Jahre gültig.",
        "Konrad Adenauer war der erste Bundeskanzler der Bundesrepublik Deutschland.",
        "Paris ist die Hauptstadt von Frankreich und liegt an der Seine."
    ]
})

def classify_hallucination(question, response, expected_answer, context):
    system_msg = "Du bist ein Experte für RAG-Halluzinationserkennung. \
Klassifiziere die Art der Halluzination anhand von Frage, Antwort, Referenzantwort und Kontext. \
Nutze eine der folgenden Kategorien: \
'Intrinsic', 'Extrinsic', 'Factuality', 'Faithfulness', 'Factual Mirage', 'Silver Lining', oder 'Keine Halluzination'."

    user_msg = f"""Frage: {question}
Antwort: {response}
Erwartete Antwort: {expected_answer}
Kontext: {context}

Bitte antworte im JSON-Format:
{{
  "hallucination_type": "<Typ>",
  "explanation": "<kurze Begründung>"
}}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2
        )
        result = response.output_text
        return eval(result)  # Vorsicht: eval nur bei eigenem kontrollierten Output
    except Exception as e:
        print(f"Fehler bei Anfrage: {e}")
        return {"hallucination_type": "Fehler", "explanation": str(e)}

# Neue Spalten für Klassifikation
df["hallucination_type"] = ""
df["explanation"] = ""

# Klassifiziere jede Zeile
for idx, row in df.iterrows():
    print(f"Verarbeite Frage {idx + 1}/{len(df)} ...")
    result = classify_hallucination(
        row["question"],
        row["response"],
        row["expected_answer"],
        row["contexts"]
    )
    df.at[idx, "hallucination_type"] = result.get("hallucination_type", "Fehler")
    df.at[idx, "explanation"] = result.get("explanation", "Keine Angabe")
    time.sleep(1.2)  # Rate Limit einhalten

# Ausgabe anzeigen
print(df[["question", "hallucination_type", "explanation"]])
