from infrastructure.llm.chat_prompts import build_feedback_prompt


def test_chat_feedback_prompt_includes_message():
    message = "I goed to school yesterday."
    prompt = build_feedback_prompt(message)
    assert message in prompt
    assert "corrections" in prompt
    assert "recommendations" in prompt
