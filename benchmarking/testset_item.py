class TestsetItem:
    query: str
    expected_answer: str
    expected_contexts: list[str]

    def __init__(self, halluzinations_art, expected_answer, expected_contexts):
        self.halluzinations_art = halluzinations_art
        self.expected_answer = expected_answer
        self.expected_contexts = expected_contexts