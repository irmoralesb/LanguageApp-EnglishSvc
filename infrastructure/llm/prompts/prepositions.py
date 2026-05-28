EXERCISE_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates exercises for small function words "
    "(prepositions like on/in/at, and similar word types). "
    "Always respond with valid JSON only, matching the requested schema."
)

EXERCISE_GENERATION_USER = """\
Create a writing exercise for the {term_type} "{practice_term}".

Definition: {definition}
Native language of the learner: {native_language}
Target language for their answer: {target_language}
{situation_line}

Return JSON with exactly these keys:
{{
  "scenario_native": "<1-2 sentences in {native_language} describing an everyday situation>",
  "sentence_native": "<One sentence in {native_language} that the learner should translate; it should naturally invite using '{practice_term}' in {target_language}>",
  "sentence_target": "<The same idea translated to {target_language}, using '{practice_term}' correctly>"
}}
"""

EXERCISE_EVALUATION_SYSTEM = (
    "You are a language teaching assistant that evaluates student answers for grammar-word exercises. "
    "Always respond with valid JSON only, matching the requested schema."
)

EXERCISE_EVALUATION_USER = """\
The student is practicing the {term_type} "{practice_term}" in {target_language}.

Reference sentence (model answer): {sentence_target}
Student's answer: {user_answer}

Evaluate whether the student correctly used "{practice_term}" (as a {term_type}) in their sentence.
The wording does not need to match the reference exactly, but the word choice must be correct and the meaning appropriate.

Return JSON with exactly these keys:
{{
  "is_correct": <true or false>,
  "feedback": "<Short constructive feedback in {target_language}>",
  "correct_example": "<Optional improved sentence if incorrect; null if correct>"
}}
"""


def build_exercise_prompt(
    practice_term: str,
    term_type: str,
    definition: str,
    native_language: str,
    target_language: str,
    situation: str | None = None,
) -> str:
    situation_line = (
        f"Optional context to reflect in the scenario: {situation}."
        if situation
        else "Pick a clear, concrete everyday context."
    )
    return EXERCISE_GENERATION_USER.format(
        practice_term=practice_term,
        term_type=term_type,
        definition=definition,
        native_language=native_language,
        target_language=target_language,
        situation_line=situation_line,
    )


def build_evaluation_prompt(
    practice_term: str,
    term_type: str,
    target_language: str,
    sentence_target: str,
    user_answer: str,
) -> str:
    return EXERCISE_EVALUATION_USER.format(
        practice_term=practice_term,
        term_type=term_type,
        target_language=target_language,
        sentence_target=sentence_target,
        user_answer=user_answer,
    )

