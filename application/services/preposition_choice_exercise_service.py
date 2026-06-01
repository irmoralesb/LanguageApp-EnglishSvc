import random as rand_mod
from uuid import UUID

from domain.entities.preposition_choice_exercise_model import (
    PrepositionChoiceEvaluation,
    PrepositionChoiceExercisePrompt,
    PrepositionChoiceHistoryRecord,
    PrepositionChoicePairStats,
)
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.practice_term_repository import PracticeTermRepositoryInterface
from domain.interfaces.preposition_choice_exercise_repository import (
    PrepositionChoiceExerciseRepositoryInterface,
)
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from domain.preposition_choice_pairs import SIMILAR_PREPOSITION_PAIRS, pair_key
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)


def _normalize_answer(value: str) -> str:
    return value.strip().lower()


class PrepositionChoiceExerciseService:

    def __init__(
        self,
        exercise_repo: PrepositionChoiceExerciseRepositoryInterface,
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

    async def _catalog_terms(self) -> set[str]:
        catalog = await self.practice_term_repo.get_catalog(skip=0, limit=500)
        return {pt.term.strip().lower() for pt in catalog}

    async def _selected_terms(self, user_id: UUID) -> set[str]:
        selections = await self.user_profile_repo.get_practice_term_selections(user_id)
        terms: set[str] = set()
        for sel in selections:
            pt = await self.practice_term_repo.get_by_id(sel.practice_term_id)
            if pt is not None:
                terms.add(pt.term.strip().lower())
        return terms

    async def _eligible_pairs(
        self, user_id: UUID,
    ) -> list[tuple[str, str]]:
        catalog_terms = await self._catalog_terms()
        selected_terms = await self._selected_terms(user_id)
        focus_terms = selected_terms if selected_terms else catalog_terms

        eligible = [
            pair
            for pair in SIMILAR_PREPOSITION_PAIRS
            if pair[0] in catalog_terms
            and pair[1] in catalog_terms
            and (pair[0] in focus_terms or pair[1] in focus_terms)
        ]
        return eligible

    async def _pick_pair(self, user_id: UUID) -> tuple[str, str]:
        eligible = await self._eligible_pairs(user_id)
        if not eligible:
            raise ExerciseGenerationError(
                "Select at least one preposition that belongs to a confusable pair "
                "(for example 'in' or 'into').",
            )

        stats = await self.exercise_repo.get_pair_stats_by_user(user_id)
        stats_by_key = {pair_key(s.option_a, s.option_b): s for s in stats}

        weights: list[float] = []
        for option_a, option_b in eligible:
            stat = stats_by_key.get(pair_key(option_a, option_b))
            incorrect = stat.incorrect_count if stat else 0
            weights.append(1.0 + incorrect * 3.0)

        return rand_mod.choices(eligible, weights=weights, k=1)[0]

    async def generate(
        self,
        user_id: UUID,
        target_language_code: str,
    ) -> tuple[PrepositionChoiceExercisePrompt, str]:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        option_a, option_b = await self._pick_pair(user_id)

        prompt = await self.llm.generate_preposition_choice_exercise(
            option_a=option_a,
            option_b=option_b,
            native_language=native_lang.name,
            target_language=target_language_code,
        )
        prompt.option_a = option_a
        prompt.option_b = option_b
        prompt.target_language_code = target_language_code

        correct = _normalize_answer(prompt.correct_preposition)
        if correct not in {option_a, option_b}:
            raise ExerciseGenerationError(
                "Generated exercise used a preposition outside the allowed pair.",
            )

        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "option_a": option_a,
                "option_b": option_b,
                "target_language_code": target_language_code,
                "scenario_native": prompt.scenario_native,
                "sentence_with_blank": prompt.sentence_with_blank,
                "sentence_complete": prompt.sentence_complete,
                "correct_preposition": correct,
            }
        )
        return prompt, token

    async def evaluate(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
    ) -> PrepositionChoiceEvaluation:
        try:
            payload = self.prompt_token_svc.verify(prompt_token)
        except InvalidPromptToken as exc:
            raise ExerciseGenerationError(f"Invalid or expired exercise token: {exc}")

        if payload.get("user_id") != str(user_id):
            raise ExerciseGenerationError("Exercise token does not belong to this user.")

        option_a = str(payload.get("option_a") or "").strip().lower()
        option_b = str(payload.get("option_b") or "").strip().lower()
        target_language_code = str(payload.get("target_language_code") or "")
        scenario_native = str(payload.get("scenario_native") or "")
        sentence_with_blank = str(payload.get("sentence_with_blank") or "")
        sentence_complete = str(payload.get("sentence_complete") or "")
        correct_preposition = _normalize_answer(str(payload.get("correct_preposition") or ""))

        if not option_a or not option_b or not sentence_with_blank or not correct_preposition:
            raise ExerciseGenerationError("Exercise token is missing required fields.")

        normalized_user = _normalize_answer(user_answer)
        is_correct = normalized_user == correct_preposition

        if is_correct:
            feedback = (
                f'Correct! "{correct_preposition}" fits this sentence.'
            )
        else:
            feedback = await self.llm.explain_preposition_choice_mistake(
                option_a=option_a,
                option_b=option_b,
                sentence_with_blank=sentence_with_blank,
                user_answer=normalized_user,
                correct_preposition=correct_preposition,
                target_language=target_language_code,
            )

        record = PrepositionChoiceHistoryRecord(
            id=None,
            user_id=user_id,
            option_a=option_a,
            option_b=option_b,
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            sentence_with_blank=sentence_with_blank,
            sentence_complete=sentence_complete,
            correct_preposition=correct_preposition,
            user_answer=normalized_user,
            is_correct=is_correct,
            feedback=feedback,
        )
        await self.exercise_repo.save_result(record)

        return PrepositionChoiceEvaluation(
            is_correct=is_correct,
            feedback=feedback,
            correct_preposition=None if is_correct else correct_preposition,
            sentence_complete=None if is_correct else sentence_complete,
        )

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[PrepositionChoiceHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)

    async def get_stats(self, user_id: UUID) -> list[PrepositionChoicePairStats]:
        return await self.exercise_repo.get_pair_stats_by_user(user_id)
