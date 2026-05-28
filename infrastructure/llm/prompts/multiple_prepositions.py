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
