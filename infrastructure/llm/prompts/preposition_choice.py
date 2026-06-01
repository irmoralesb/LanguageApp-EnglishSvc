PREPOSITION_CHOICE_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates fill-in-the-blank exercises "
    "where learners must choose between two similar English prepositions. "
    "Always respond with valid JSON only, matching the requested schema."
)

PREPOSITION_CHOICE_GENERATION_USER = """\
Create a fill-in-the-blank exercise in {target_language}.

The learner must choose between "{option_a}" and "{option_b}".
Use exactly one blank marker "___" in the sentence where the preposition belongs.
The correct answer must be exactly one of those two words (no other preposition).

{native_context_line}

Return JSON with exactly these keys:
{{
  "scenario_native": "<1 short sentence in {native_language} describing the situation, or empty string>",
  "sentence_with_blank": "<One {target_language} sentence with exactly one '___' where the preposition goes>",
  "correct_preposition": "<either '{option_a}' or '{option_b}'>",
  "sentence_complete": "<The same sentence with the correct preposition filled in (no blank)>"
}}
"""

PREPOSITION_CHOICE_FEEDBACK_SYSTEM = (
    "You are a concise English grammar tutor. "
    "Always respond with valid JSON only, matching the requested schema."
)

PREPOSITION_CHOICE_FEEDBACK_USER = """\
The learner had to choose between "{option_a}" and "{option_b}" in this sentence:

"{sentence_with_blank}"

They answered: "{user_answer}"
The correct answer is: "{correct_preposition}"

Explain briefly why "{correct_preposition}" fits and why "{user_answer}" does not in this context.
Keep feedback under 3 sentences in {target_language}.

Return JSON:
{{
  "feedback": "<constructive explanation>"
}}
"""


def build_preposition_choice_generation_prompt(
    option_a: str,
    option_b: str,
    native_language: str,
    target_language: str,
) -> str:
    native_context_line = (
        f"The learner's native language is {native_language}; "
        "the scenario_native field should be in that language."
    )
    return PREPOSITION_CHOICE_GENERATION_USER.format(
        option_a=option_a,
        option_b=option_b,
        native_language=native_language,
        target_language=target_language,
        native_context_line=native_context_line,
    )


def build_preposition_choice_feedback_prompt(
    option_a: str,
    option_b: str,
    sentence_with_blank: str,
    user_answer: str,
    correct_preposition: str,
    target_language: str,
) -> str:
    return PREPOSITION_CHOICE_FEEDBACK_USER.format(
        option_a=option_a,
        option_b=option_b,
        sentence_with_blank=sentence_with_blank,
        user_answer=user_answer,
        correct_preposition=correct_preposition,
        target_language=target_language,
    )
