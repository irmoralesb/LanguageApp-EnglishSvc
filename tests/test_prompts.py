"""Unit tests for infrastructure.llm.prompts."""

from infrastructure.llm.prompts import (
    EXERCISE_GENERATION_SYSTEM,
    build_exercise_prompt,
    build_evaluation_prompt,
)


def test_system_prompt_is_non_empty() -> None:
    assert EXERCISE_GENERATION_SYSTEM
    assert "JSON" in EXERCISE_GENERATION_SYSTEM


def test_build_exercise_prompt_contains_inputs() -> None:
    msg = build_exercise_prompt(
        practice_term="on",
        term_type="preposition",
        definition="Used for days and surfaces",
        native_language="es",
        target_language="en",
        situation="work",
    )
    assert "on" in msg
    assert "preposition" in msg
    assert "Used for days" in msg
    assert "es" in msg and "en" in msg
    assert "work" in msg.lower() or "context" in msg.lower()


def test_build_exercise_prompt_without_situation() -> None:
    msg = build_exercise_prompt(
        practice_term="in",
        term_type="preposition",
        definition="Used for enclosed spaces",
        native_language="de",
        target_language="en",
        situation=None,
    )
    assert "in" in msg
    assert "everyday" in msg.lower() or "pick" in msg.lower()


def test_build_evaluation_prompt_contains_sentence_and_answer() -> None:
    msg = build_evaluation_prompt(
        practice_term="at",
        term_type="preposition",
        target_language="en",
        sentence_target="We arrived at noon.",
        user_answer="We arrived on noon.",
    )
    assert "at" in msg
    assert "We arrived at noon." in msg
    assert "We arrived on noon." in msg
