from infrastructure.llm.prompts import build_evaluation_prompt, build_exercise_prompt


def test_build_prepositions_exercise_prompt_contains_inputs():
    prompt = build_exercise_prompt(
        practice_term="in",
        term_type="preposition",
        definition="inside an area",
        native_language="Spanish",
        target_language="English",
        situation="office",
    )
    assert "in" in prompt
    assert "inside an area" in prompt
    assert "Spanish" in prompt
    assert "English" in prompt


def test_build_prepositions_evaluation_prompt_contains_inputs():
    prompt = build_evaluation_prompt(
        practice_term="at",
        term_type="preposition",
        target_language="English",
        sentence_target="She is at school.",
        user_answer="She is in school.",
    )
    assert "She is at school." in prompt
    assert "She is in school." in prompt
