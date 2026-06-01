from infrastructure.llm.prompts.preposition_choice import (
    build_preposition_choice_generation_prompt,
    build_preposition_choice_feedback_prompt,
)


def test_generation_prompt_includes_both_options() -> None:
    prompt = build_preposition_choice_generation_prompt(
        option_a="in",
        option_b="into",
        native_language="Spanish",
        target_language="English",
    )
    assert '"in"' in prompt
    assert '"into"' in prompt
    assert "___" in prompt


def test_feedback_prompt_includes_learner_answer() -> None:
    prompt = build_preposition_choice_feedback_prompt(
        option_a="in",
        option_b="into",
        sentence_with_blank="The fruit is ___ the table.",
        user_answer="in",
        correct_preposition="into",
        target_language="English",
    )
    assert "The fruit is ___ the table." in prompt
    assert "into" in prompt
