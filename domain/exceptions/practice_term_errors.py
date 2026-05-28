from uuid import UUID


class PracticeTermNotFoundError(Exception):
    def __init__(self, practice_term_id: UUID):
        self.practice_term_id = practice_term_id
        super().__init__(f"Practice term with id '{practice_term_id}' not found.")


class PracticeTermAlreadyExistsError(Exception):
    def __init__(self, term: str, term_type: str):
        self.term = term
        self.term_type = term_type
        super().__init__(f"Practice term '{term}' (type '{term_type}') already exists.")
