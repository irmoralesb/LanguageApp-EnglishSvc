from infrastructure.llm.phrasal_verbs_prompts import (
    build_evaluation_prompt,
    build_exercise_prompt,
)


def test_build_phrasal_exercise_prompt_contains_inputs():
    prompt = build_exercise_prompt(
        phrasal_verb="look up",
        definition="search for information",
        native_language="Spanish",
        target_language="English",
        situation="at school",
    )
    assert "look up" in prompt
    assert "search for information" in prompt
    assert "Spanish" in prompt
    assert "English" in prompt


def test_build_phrasal_evaluation_prompt_contains_expected_fields():
    prompt = build_evaluation_prompt(
        phrasal_verb="give up",
        target_language="English",
        sentence_target="He gave up smoking.",
        user_answer="He give up smoking.",
    )
    assert "give up" in prompt
    assert "He gave up smoking." in prompt
    assert "He give up smoking." in prompt
