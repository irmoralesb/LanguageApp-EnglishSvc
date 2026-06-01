from uuid import UUID


class EnglishExpressionNotFoundError(Exception):
    def __init__(self, english_expression_id: UUID):
        self.english_expression_id = english_expression_id
        super().__init__(f"English expression {english_expression_id} not found.")
