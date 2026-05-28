import random as rand_mod
from uuid import UUID

from domain.entities.multiple_prepositions_exercise_model import (
    MultiplePrepositionsExercisePrompt,
    MultiplePrepositionsEvaluation,
    MultiplePrepositionsExerciseHistoryRecord,
)
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.multiple_prepositions_exercise_repository import (
    MultiplePrepositionsExerciseRepositoryInterface,
)
from domain.interfaces.practice_term_repository import PracticeTermRepositoryInterface
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)


# How many distinct user-selected prepositions to combine per exercise.
_MIN_TERMS_PER_EXERCISE = 2
_MAX_TERMS_PER_EXERCISE = 3


class MultiplePrepositionsExerciseService:

    def __init__(
        self,
        exercise_repo: MultiplePrepositionsExerciseRepositoryInterface,
        practice_term_repo: PracticeTermRepositoryInterface,
        user_profile_repo: UserProfileRepositoryInterface,
        language_repo: LanguageRepositoryInterface,
        llm_provider: LLMProviderInterface,
        prompt_token_svc: PromptTokenService,
    ):
        self.exercise_repo = exercise_repo
        self.practice_term_repo = practice_term_repo
        self.user_profile_repo = user_profile_repo
        self.language_repo = language_repo
        self.llm = llm_provider
        self.prompt_token_svc = prompt_token_svc

    async def generate(
        self,
        user_id: UUID,
        target_language_code: str,
    ) -> tuple[MultiplePrepositionsExercisePrompt, str]:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        selections = await self.user_profile_repo.get_practice_term_selections(user_id)
        if not selections or len(selections) < _MIN_TERMS_PER_EXERCISE:
            raise ExerciseGenerationError(
                "Select at least 2 prepositions to use this exercise.",
            )

        sample_size = min(_MAX_TERMS_PER_EXERCISE, len(selections))
        if sample_size > _MIN_TERMS_PER_EXERCISE:
            sample_size = rand_mod.randint(_MIN_TERMS_PER_EXERCISE, sample_size)
        chosen = rand_mod.sample(selections, sample_size)

        terms = []
        for sel in chosen:
            pt = await self.practice_term_repo.get_by_id(sel.practice_term_id)
            if pt is None:
                continue
            terms.append(pt)
        if len(terms) < _MIN_TERMS_PER_EXERCISE:
            raise ExerciseGenerationError(
                "Unable to load enough selected prepositions to build the exercise.",
            )

        prompt = await self.llm.generate_multiple_prepositions_exercise(
            practice_terms=[t.term for t in terms],
            native_language=native_lang.name,
            target_language=target_language_code,
        )
        prompt.practice_term_ids = [t.id for t in terms if t.id is not None]
        prompt.practice_term_texts = [t.term for t in terms]
        prompt.target_language_code = target_language_code

        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "practice_term_ids": [str(tid) for tid in prompt.practice_term_ids],
                "practice_term_texts": prompt.practice_term_texts,
                "target_language_code": target_language_code,
                "sentence_native": prompt.sentence_native,
                "sentence_target": prompt.sentence_target,
            }
        )
        return prompt, token

    async def evaluate(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
        attempt_number: int,
    ) -> MultiplePrepositionsEvaluation:
        try:
            payload = self.prompt_token_svc.verify(prompt_token)
        except InvalidPromptToken as exc:
            raise ExerciseGenerationError(f"Invalid or expired exercise token: {exc}")

        if payload.get("user_id") != str(user_id):
            raise ExerciseGenerationError("Exercise token does not belong to this user.")

        practice_term_texts: list[str] = list(payload.get("practice_term_texts") or [])
        practice_term_ids = [UUID(s) for s in (payload.get("practice_term_ids") or [])]
        target_language_code = str(payload.get("target_language_code") or "")
        sentence_native = str(payload.get("sentence_native") or "")
        sentence_target = str(payload.get("sentence_target") or "")

        if not practice_term_texts or not sentence_native or not sentence_target:
            raise ExerciseGenerationError("Exercise token is missing required fields.")

        evaluation = await self.llm.evaluate_multiple_prepositions(
            practice_terms=practice_term_texts,
            target_language=target_language_code,
            sentence_native=sentence_native,
            sentence_target=sentence_target,
            user_answer=user_answer,
            attempt_number=attempt_number,
        )

        # Stateless reveal rule: only show the reference translation when the
        # answer is correct OR the learner has already used their second try.
        reveal = evaluation.is_correct or attempt_number >= 2
        if reveal:
            evaluation.correct_sentence_target = sentence_target

        record = MultiplePrepositionsExerciseHistoryRecord(
            id=None,
            user_id=user_id,
            practice_term_ids=practice_term_ids,
            target_language_code=target_language_code,
            sentence_native=sentence_native,
            sentence_target=sentence_target,
            user_answer=user_answer,
            attempt_number=attempt_number,
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
            revealed=reveal,
        )
        await self.exercise_repo.save_attempt(record)

        return evaluation

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[MultiplePrepositionsExerciseHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)
