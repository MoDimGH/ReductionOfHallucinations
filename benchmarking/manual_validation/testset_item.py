class TestsetItem:
    query: str
    expected_answer: str
    expected_contexts: list[str]

    def __init__(self, query, expected_answer, expected_contexts):
        self.query = query
        self.expected_answer = expected_answer
        self.expected_contexts = expected_contexts