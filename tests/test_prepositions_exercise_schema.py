import pytest
from pydantic import ValidationError

from application.schemas.exercise_schema import ExerciseAnswerRequest, ExerciseRequest


def test_prepositions_request_accepts_without_term_id():
    payload = ExerciseRequest(target_language_code="en")
    assert payload.practice_term_id is None


def test_prepositions_answer_requires_non_empty_user_answer():
    with pytest.raises(ValidationError):
        ExerciseAnswerRequest(
            practice_term_id="00000000-0000-0000-0000-000000000001",
            target_language_code="en",
            scenario_native="escenario",
            sentence_native="oracion",
            sentence_target="target sentence",
            user_answer="",
        )
