import pytest
from pydantic import ValidationError

from application.schemas.preposition_choice_exercise_schema import (
    PrepositionChoiceAnswerRequest,
    PrepositionChoiceExerciseRequest,
    PrepositionChoiceEvaluationResponse,
)


def test_generate_request_requires_target_language() -> None:
    with pytest.raises(ValidationError):
        PrepositionChoiceExerciseRequest(target_language_code="e")
    r = PrepositionChoiceExerciseRequest(target_language_code="en")
    assert r.target_language_code == "en"


def test_answer_request_requires_token_and_answer() -> None:
    with pytest.raises(ValidationError):
        PrepositionChoiceAnswerRequest(prompt_token="", user_answer="in")
    with pytest.raises(ValidationError):
        PrepositionChoiceAnswerRequest(prompt_token="t", user_answer="")


def test_evaluation_response_optional_reveal_fields() -> None:
    ok = PrepositionChoiceEvaluationResponse(is_correct=True, feedback="Great")
    assert ok.correct_preposition is None
    assert ok.sentence_complete is None

    wrong = PrepositionChoiceEvaluationResponse(
        is_correct=False,
        feedback="Try into for movement",
        correct_preposition="into",
        sentence_complete="The fruit is into the bowl.",
    )
    assert wrong.correct_preposition == "into"
