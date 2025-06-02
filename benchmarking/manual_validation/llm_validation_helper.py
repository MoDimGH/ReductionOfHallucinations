from benchmarking.manual_validation.datahandler import DataHandler

"""Hier ist die Antwort, die du mir vorhin gegeben hast: {expected_answer}

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


def query(query):
    return DataHandler.model.invoke(query)


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