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


MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates translation exercises focused on "
    "preposition usage. Always respond with valid JSON only, matching the requested schema."
)

MULTIPLE_PREPOSITIONS_GENERATION_USER = """\
Create a translation exercise that forces the learner to use SEVERAL specific prepositions.

Required prepositions (the learner must use ALL of these, in {target_language}, when translating):
{prepositions_list}

Native language of the learner: {native_language}
Target language for their translation: {target_language}

Produce one natural, everyday sentence in {native_language} whose correct translation to
{target_language} naturally and unambiguously requires using ALL of the prepositions listed
above. The sentence should be 1-2 clauses long, concrete, and not contrived.

Return JSON with exactly these keys:
{{
  "sentence_native": "<one sentence in {native_language}>",
  "sentence_target": "<the correct translation to {target_language}, using each required preposition>",
  "used_prepositions": ["<each required preposition that appears in sentence_target, lowercase>"]
}}
"""

MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM = (
    "You are a language teaching assistant that evaluates translations, focusing primarily on "
    "correct preposition usage. Always respond with valid JSON only, matching the requested schema. "
    "Do NOT include the correct full sentence in your feedback text; the application controls "
    "when (and whether) to reveal the reference translation to the learner."
)

MULTIPLE_PREPOSITIONS_EVALUATION_USER = """\
The learner is translating from {native_language_or_source} into {target_language}.

Native sentence shown to the learner:
{sentence_native}

Reference translation (model answer, KEEP CONFIDENTIAL - never quote it verbatim in feedback):
{sentence_target}

Required prepositions the learner must use correctly in {target_language}:
{prepositions_list}

Learner's translation:
{user_answer}

Evaluate the learner's translation. The PRIMARY criterion is whether each required
preposition is used correctly (right preposition for the right relationship/idiom). Other
issues (vocabulary, word order, articles, minor typos) should be reported separately as
"minor_issues" and should NOT, by themselves, mark the answer incorrect if all required
prepositions are used correctly and the meaning is preserved.

Return JSON with exactly these keys:
{{
  "is_correct": <true if all required prepositions are used correctly AND the meaning is preserved>,
  "feedback": "<short overall feedback in {target_language}; do NOT quote the reference translation>",
  "preposition_feedback": [
    {{"preposition": "<one of the required prepositions>",
      "used_correctly": <true or false>,
      "explanation": "<short explanation of why it is right or wrong, and what is correct usage; do NOT quote the reference translation>"}}
  ],
  "minor_issues": ["<short note for each minor issue, if any>"]
}}
"""


def build_multiple_prepositions_generation_prompt(
    prepositions: list[str],
    native_language: str,
    target_language: str,
) -> str:
    prepositions_list = "\n".join(f"- {p}" for p in prepositions)
    return MULTIPLE_PREPOSITIONS_GENERATION_USER.format(
        prepositions_list=prepositions_list,
        native_language=native_language,
        target_language=target_language,
    )


def build_multiple_prepositions_evaluation_prompt(
    prepositions: list[str],
    native_language_or_source: str,
    target_language: str,
    sentence_native: str,
    sentence_target: str,
    user_answer: str,
) -> str:
    prepositions_list = "\n".join(f"- {p}" for p in prepositions)
    return MULTIPLE_PREPOSITIONS_EVALUATION_USER.format(
        prepositions_list=prepositions_list,
        native_language_or_source=native_language_or_source,
        target_language=target_language,
        sentence_native=sentence_native,
        sentence_target=sentence_target,
        user_answer=user_answer,
    )
