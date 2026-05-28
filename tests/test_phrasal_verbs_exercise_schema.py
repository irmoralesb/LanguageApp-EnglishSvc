import pytest
from pydantic import ValidationError

from application.schemas.phrasal_verb_exercise_schema import (
    ExerciseAnswerRequest,
    ExerciseRequest,
)


def test_phrasal_request_accepts_optional_id():
    payload = ExerciseRequest(target_language_code="en")
    assert payload.phrasal_verb_id is None


def test_phrasal_answer_requires_user_answer():
    with pytest.raises(ValidationError):
        ExerciseAnswerRequest(
            phrasal_verb_id="00000000-0000-0000-0000-000000000001",
            target_language_code="en",
            scenario_native="escenario",
            sentence_native="oracion",
            sentence_target="target sentence",
            user_answer="",
        )
