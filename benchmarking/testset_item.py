class TestsetItem:
    query: str
    expected_answer: str
    expected_contexts: list[str]


    def __init__(self, halluzinations_art="", generierte_query="", provokations_erlaeuterung="", generierte_ground_truth_antwort="", abgerufene_quellen=""):
        self.halluzinations_art = halluzinations_art
        self.generierte_query = generierte_query
        self.provokations_erlaeuterung = provokations_erlaeuterung
        self.generierte_ground_truth_antwort = generierte_ground_truth_antwort
        self.abgerufene_quellen = abgerufene_quellen