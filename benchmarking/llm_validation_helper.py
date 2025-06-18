import json

from langchain.prompts import ChatPromptTemplate

from benchmarking.datahandler import DataHandler
from rag_pipeline.constants import (
    TESTSET_HELPER_PROMPT_PARAM_IS_QUERY_SUPPORTED_KW,
    TESTSET_HELPER_PROMPT_PARAM_ALTERNATIVE_QUERIES_KW
)


def with_n_retrys(n, func):
    for _ in range(n):
        try:
            return func()
        except:
            pass
    return None


def query_model(query) -> list[str]:
    answers = []
    for i in range(3):
        answer = with_n_retrys(3, lambda: DataHandler.get_generation_model().invoke(query))
        if answer:
            answers.append(answer.content)
            
    return answers


def validate_testset_user_input(query, reference_contexts) -> list[dict]:
    prompt_template = ChatPromptTemplate.from_template(
        """
        Bitte prüfe, ob die Frage des Nutzers vollständig mit den Informationen aus den Referenzen beantwortet werden kann. Wenn dies nicht der Fall ist, gib bitte eine alternative Frage an, welche wirklich vollständig mit den Referenzen beantwortet werden kann.
        
        --------

        Nutzerfrage: {query}

        --------

        Referenzen: {reference_contexts}

        --------

        Outputformat:
        {{
            "wirdGanzBeantwortet": <true/false>,
            "grund": <Beschreibung des Grundes>,
            "alternativeFrage": <null|alternative Frage>
        }}
        """
    )
    prompt = prompt_template.format(query=query, reference_contexts=reference_contexts)
    answers = query_model(prompt)

    validation_results = []
    for answer in answers:
        validation_result = json.loads(answer)
        validation_results.append(validation_result)

    return validation_results


def validate_testset_user_input(query, reference_contexts) -> list[dict]:
    prompt_template = ChatPromptTemplate.from_template(
        """
        Bitte prüfe, ob die Frage des Nutzers vollständig mit den Informationen aus den Referenzen beantwortet werden kann. Wenn dies nicht der Fall ist, gib bitte eine alternative Frage an, welche wirklich vollständig mit den Referenzen beantwortet werden kann.
        
        --------

        Nutzerfrage: {query}

        --------

        Referenzen: {reference_contexts}

        --------

        Outputformat:
        {{
            "wirdGanzBeantwortet": <true/false>,
            "grund": <Beschreibung des Grundes>,
            "alternativeFrage": <null|alternative Frage>
        }}
        """
    )
    prompt = prompt_template.format(query=query, reference_contexts=reference_contexts)
    answers = query_model(prompt)

    validation_results = []
    for answer in answers:
        validation_result = json.loads(answer)
        validation_results.append(validation_result)

    return validation_results

    # Möglichkeiten ein RAG-System auf Halluzinationen zu evaluieren:
    # 1. RAGAS Testset mit Query, Antwort und Referenzen generieren (sichergestellt dass es 100% stimmt)
    # 2. Antworten vom RAG-System generieren lassen
    # 3. Anhand des Vergleichs der erwarteten und wirklichen Antworten bewerten, ob und welche Halluzinationen auftreten

    # Nun ist die Frage: wie erstelle ich ein 100% stimmiges Testset?
    # -> Vorgenerierung durch RAGAS mit Openai und openai rag! (je 10 mehr, gleichmäßig verteilt auf datensatzgrößen)
    #   -> erstellung von openai vector dbs für jeden usecases
    #   -> >ergänzen< der reference_contexts um contexts die bei einer normalen openai rag query generiert werden
    # -> heranziehen von openai zur bewertung (je 3x) der vorgenerierten user_input und reference, sowie zur korrektur dieser
    # -> manuelle Sichtung des Testdatensatzes und korrektur der Fragen/antworten bzw. wegstreichen bei ungehaltvollen contexts
    # => ground truth hergestellt!

    # Vorgehen:
    # /1. openai vector dbs erstellen
    # /2. Erstellen von ragas testbenches aus den dokumenten der vector dbs
    # /3. Ergänzen der Ragas testbenches um reference_contexts aus openai rag
    # 4. Openai Bewertungen des User Input und der References erstellen (auch selbstständiges script)
    # 5. UI zum Bearbeiten der Testbenchdaten auf Basis der Openai Bewertungen erstellen
    # verbesserung: 6. fuer jede Art halluzinations-provozierende Testset Queries generieren
    # => Ground truth
