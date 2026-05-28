"""Pydantic schema validation tests for the multiple-prepositions exercise."""

import pytest
from pydantic import ValidationError

from application.schemas.multiple_prepositions_exercise_schema import (
    MultiplePrepositionsAnswerRequest,
    MultiplePrepositionsEvaluationResponse,
    MultiplePrepositionsExerciseRequest,
)


def test_generate_request_requires_target_language() -> None:
    with pytest.raises(ValidationError):
        MultiplePrepositionsExerciseRequest(target_language_code="e")
    r = MultiplePrepositionsExerciseRequest(target_language_code="en")
    assert r.target_language_code == "en"


def test_answer_request_attempt_number_must_be_1_or_2() -> None:
    base = dict(prompt_token="abc.def", user_answer="hello")
    MultiplePrepositionsAnswerRequest(**base, attempt_number=1)
    MultiplePrepositionsAnswerRequest(**base, attempt_number=2)
    with pytest.raises(ValidationError):
        MultiplePrepositionsAnswerRequest(**base, attempt_number=0)
    with pytest.raises(ValidationError):
        MultiplePrepositionsAnswerRequest(**base, attempt_number=3)


def test_answer_request_requires_token_and_answer() -> None:
    with pytest.raises(ValidationError):
        MultiplePrepositionsAnswerRequest(
            prompt_token="", user_answer="x", attempt_number=1,
        )
    with pytest.raises(ValidationError):
        MultiplePrepositionsAnswerRequest(
            prompt_token="t", user_answer="", attempt_number=1,
        )


def test_evaluation_response_correct_sentence_optional() -> None:
    ok = MultiplePrepositionsEvaluationResponse(
        is_correct=True,
        feedback="Great",
        attempt_number=1,
    )
    assert ok.correct_sentence_target is None
    assert ok.preposition_feedback == []
    assert ok.minor_issues == []

    revealed = MultiplePrepositionsEvaluationResponse(
        is_correct=False,
        feedback="Try again",
        attempt_number=2,
        correct_sentence_target="The book is on the table.",
    )
    assert revealed.correct_sentence_target == "The book is on the table."
