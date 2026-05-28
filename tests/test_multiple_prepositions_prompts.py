"""Unit tests for the multiple-prepositions LLM prompts and PromptTokenService."""

import pytest

from application.services.prompt_token_service import (
    InvalidPromptToken,
    PromptTokenService,
)
from infrastructure.llm.prompts import (
    MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM,
    MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM,
    build_multiple_prepositions_generation_prompt,
    build_multiple_prepositions_evaluation_prompt,
)


def test_system_prompts_are_non_empty_and_request_json() -> None:
    assert MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM
    assert "JSON" in MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM
    assert MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM
    assert "JSON" in MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM


def test_evaluation_system_prompt_keeps_reference_confidential() -> None:
    msg = MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM.lower()
    assert "do not" in msg or "confidential" in msg or "never" in msg


def test_generation_prompt_lists_all_prepositions() -> None:
    msg = build_multiple_prepositions_generation_prompt(
        prepositions=["on", "in", "at"],
        native_language="Spanish",
        target_language="en",
    )
    assert "Spanish" in msg
    assert "en" in msg
    for p in ("on", "in", "at"):
        assert f"- {p}" in msg


def test_evaluation_prompt_includes_answer_and_required_words() -> None:
    msg = build_multiple_prepositions_evaluation_prompt(
        prepositions=["on", "by"],
        native_language_or_source="Spanish",
        target_language="en",
        sentence_native="El libro esta sobre la mesa, escrito por Maria.",
        sentence_target="The book is on the table, written by Maria.",
        user_answer="The book is in the table, written from Maria.",
    )
    assert "- on" in msg
    assert "- by" in msg
    assert "El libro" in msg
    assert "in the table" in msg


def test_prompt_token_round_trip() -> None:
    svc = PromptTokenService(secret_key="x" * 32)
    payload = {"sentence_target": "The book is on the table.", "user_id": "u1"}
    token = svc.sign(payload)
    decoded = svc.verify(token)
    assert decoded["sentence_target"] == payload["sentence_target"]
    assert decoded["user_id"] == "u1"
    assert "iat" in decoded


def test_prompt_token_rejects_tampered_payload() -> None:
    svc = PromptTokenService(secret_key="x" * 32)
    token = svc.sign({"a": 1})
    body, sig = token.split(".", 1)
    tampered = body[:-1] + ("A" if body[-1] != "A" else "B") + "." + sig
    with pytest.raises(InvalidPromptToken):
        svc.verify(tampered)


def test_prompt_token_rejects_bad_signature_with_different_key() -> None:
    a = PromptTokenService(secret_key="a" * 32)
    b = PromptTokenService(secret_key="b" * 32)
    token = a.sign({"a": 1})
    with pytest.raises(InvalidPromptToken):
        b.verify(token)


def test_prompt_token_expires() -> None:
    svc = PromptTokenService(secret_key="x" * 32, max_age_seconds=0)
    token = svc.sign({"a": 1})
    import time
    time.sleep(1.1)
    with pytest.raises(InvalidPromptToken):
        svc.verify(token)
