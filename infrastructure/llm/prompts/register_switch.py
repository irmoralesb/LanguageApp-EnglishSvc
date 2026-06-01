REGISTER_SWITCH_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates register-switch exercises. "
    "Learners rewrite a sentence to match a different level of formality or slang. "
    "Always respond with valid JSON only, matching the requested schema."
)

REGISTER_SWITCH_GENERATION_USER = """\
Create a register-switch exercise in {target_language}.

The learner's native language is {native_language}.
Target register for the learner's answer: {target_register}
{slang_line}

Provide:
1. scenario_native: short context in {native_language}
2. source_sentence: one sentence in {target_language} written in {source_register} register
3. source_register: one of formal, neutral, casual

Return JSON:
{{
  "scenario_native": "<context in {native_language}>",
  "source_sentence": "<sentence in {target_language}>",
  "source_register": "<formal|neutral|casual>"
}}
"""

REGISTER_SWITCH_EVALUATION_SYSTEM = (
    "You are a concise English coach evaluating register and tone. "
    "Always respond with valid JSON only, matching the requested schema."
)

REGISTER_SWITCH_EVALUATION_USER = """\
Scenario: {scenario_native}

Original sentence ({source_register}):
"{source_sentence}"

The learner should rewrite it in {target_register} register.
{slang_eval_line}

Learner's answer:
"{user_answer}"

Return JSON:
{{
  "is_correct": <true or false>,
  "feedback": "<brief feedback in {target_language}>",
  "model_answer": "<ideal rewrite in {target_register} register>"
}}
"""


def build_register_switch_generation_prompt(
    native_language: str,
    target_language: str,
    source_register: str,
    target_register: str,
    slang_level: str | None,
) -> str:
    slang_line = ""
    if slang_level and target_register == "casual":
        slang_line = f"Desired slang intensity when casual: {slang_level}."
    return REGISTER_SWITCH_GENERATION_USER.format(
        native_language=native_language,
        target_language=target_language,
        source_register=source_register,
        target_register=target_register,
        slang_line=slang_line,
    )


def build_register_switch_evaluation_prompt(
    scenario_native: str,
    source_sentence: str,
    source_register: str,
    target_register: str,
    slang_level: str | None,
    user_answer: str,
    target_language: str,
) -> str:
    slang_eval_line = ""
    if slang_level and target_register == "casual":
        slang_eval_line = f"Slang level expected: {slang_level}."
    return REGISTER_SWITCH_EVALUATION_USER.format(
        scenario_native=scenario_native,
        source_sentence=source_sentence,
        source_register=source_register,
        target_register=target_register,
        slang_eval_line=slang_eval_line,
        user_answer=user_answer,
        target_language=target_language,
    )
