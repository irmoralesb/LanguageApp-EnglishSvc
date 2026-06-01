NATURAL_REWRITE_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates rewrite exercises. "
    "Learners see an overly stiff or unnatural sentence and must rewrite it naturally. "
    "Always respond with valid JSON only, matching the requested schema."
)

NATURAL_REWRITE_GENERATION_USER = """\
Create a natural-rewrite exercise in {target_language}.

The learner's native language is {native_language}.

Provide:
1. A short scenario in {native_language} (scenario_native).
2. One stiff, overly formal, or awkward sentence in {target_language} (stiff_sentence).
3. A brief hint in {native_language} about what sounds unnatural (context_note).

Return JSON:
{{
  "scenario_native": "<1-2 sentences in {native_language}>",
  "stiff_sentence": "<one stiff sentence in {target_language}>",
  "context_note": "<short hint in {native_language}>"
}}
"""

NATURAL_REWRITE_EVALUATION_SYSTEM = (
    "You are a concise English writing coach evaluating rewrites. "
    "Always respond with valid JSON only, matching the requested schema."
)

NATURAL_REWRITE_EVALUATION_USER = """\
Scenario (learner's language): {scenario_native}

Stiff sentence to improve:
"{stiff_sentence}"

Learner's rewrite:
"{user_answer}"

Decide if the rewrite sounds natural in {target_language} while keeping the same meaning.
If incorrect or awkward, provide constructive feedback and a model_answer (natural version).

Return JSON:
{{
  "is_correct": <true or false>,
  "feedback": "<brief feedback in {target_language}>",
  "model_answer": "<natural rewrite in {target_language}>"
}}
"""


def build_natural_rewrite_generation_prompt(
    native_language: str,
    target_language: str,
) -> str:
    return NATURAL_REWRITE_GENERATION_USER.format(
        native_language=native_language,
        target_language=target_language,
    )


def build_natural_rewrite_evaluation_prompt(
    scenario_native: str,
    stiff_sentence: str,
    user_answer: str,
    target_language: str,
) -> str:
    return NATURAL_REWRITE_EVALUATION_USER.format(
        scenario_native=scenario_native,
        stiff_sentence=stiff_sentence,
        user_answer=user_answer,
        target_language=target_language,
    )
