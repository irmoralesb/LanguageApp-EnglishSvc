import random as rand_mod
from uuid import UUID

from domain.confusable_word_pairs import CONFUSABLE_WORD_PAIRS, pair_key
from domain.entities.confusable_word_exercise_model import (
    ConfusableWordEvaluation,
    ConfusableWordExercisePrompt,
    ConfusableWordHistoryRecord,
    ConfusableWordPairStats,
)
from domain.entities.preposition_choice_exercise_model import PrepositionChoiceExercisePrompt
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.confusable_word_exercise_repository import (
    ConfusableWordExerciseRepositoryInterface,
)
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.practice_term_repository import PracticeTermRepositoryInterface
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)


def _normalize_answer(value: str) -> str:
    return value.strip().lower()


class ConfusableWordExerciseService:

    def __init__(
        self,
        exercise_repo: ConfusableWordExerciseRepositoryInterface,
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

    async def _eligible_pairs(self, user_id: UUID) -> list[tuple[str, str]]:
        del user_id  # pairs are curated; no practice-term catalog required
        return list(CONFUSABLE_WORD_PAIRS)

    async def _pick_pair(self, user_id: UUID) -> tuple[str, str]:
        eligible = await self._eligible_pairs(user_id)
        if not eligible:
            raise ExerciseGenerationError("No confusable word pairs configured.")

        stats = await self.exercise_repo.get_pair_stats_by_user(user_id)
        stats_by_key = {pair_key(s.option_a, s.option_b): s for s in stats}

        weights: list[float] = []
        for option_a, option_b in eligible:
            stat = stats_by_key.get(pair_key(option_a, option_b))
            incorrect = stat.incorrect_count if stat else 0
            weights.append(1.0 + incorrect * 3.0)

        return rand_mod.choices(eligible, weights=weights, k=1)[0]

    @staticmethod
    def _to_confusable_prompt(
        llm_prompt: PrepositionChoiceExercisePrompt,
        option_a: str,
        option_b: str,
        target_language_code: str,
    ) -> ConfusableWordExercisePrompt:
        return ConfusableWordExercisePrompt(
            option_a=option_a,
            option_b=option_b,
            target_language_code=target_language_code,
            scenario_native=llm_prompt.scenario_native,
            sentence_with_blank=llm_prompt.sentence_with_blank,
            correct_word=_normalize_answer(llm_prompt.correct_preposition),
            sentence_complete=llm_prompt.sentence_complete,
        )

    async def generate(
        self,
        user_id: UUID,
        target_language_code: str,
    ) -> tuple[ConfusableWordExercisePrompt, str]:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        option_a, option_b = await self._pick_pair(user_id)

        llm_prompt = await self.llm.generate_preposition_choice_exercise(
            option_a=option_a,
            option_b=option_b,
            native_language=native_lang.name,
            target_language=target_language_code,
        )
        prompt = self._to_confusable_prompt(llm_prompt, option_a, option_b, target_language_code)

        correct = _normalize_answer(prompt.correct_word)
        if correct not in {option_a, option_b}:
            raise ExerciseGenerationError(
                "Generated exercise used a word outside the allowed pair.",
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
                "correct_word": correct,
            }
        )
        return prompt, token

    async def evaluate(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
    ) -> ConfusableWordEvaluation:
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
        correct_word = _normalize_answer(str(payload.get("correct_word") or ""))

        if not option_a or not option_b or not sentence_with_blank or not correct_word:
            raise ExerciseGenerationError("Exercise token is missing required fields.")

        normalized_user = _normalize_answer(user_answer)
        is_correct = normalized_user == correct_word

        if is_correct:
            feedback = f'Correct! "{correct_word}" fits this sentence.'
        else:
            feedback = await self.llm.explain_preposition_choice_mistake(
                option_a=option_a,
                option_b=option_b,
                sentence_with_blank=sentence_with_blank,
                user_answer=normalized_user,
                correct_preposition=correct_word,
                target_language=target_language_code,
            )

        record = ConfusableWordHistoryRecord(
            id=None,
            user_id=user_id,
            option_a=option_a,
            option_b=option_b,
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            sentence_with_blank=sentence_with_blank,
            sentence_complete=sentence_complete,
            correct_word=correct_word,
            user_answer=normalized_user,
            is_correct=is_correct,
            feedback=feedback,
        )
        await self.exercise_repo.save_result(record)

        return ConfusableWordEvaluation(
            is_correct=is_correct,
            feedback=feedback,
            correct_word=None if is_correct else correct_word,
            sentence_complete=None if is_correct else sentence_complete,
        )

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ConfusableWordHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)

    async def get_stats(self, user_id: UUID) -> list[ConfusableWordPairStats]:
        return await self.exercise_repo.get_pair_stats_by_user(user_id)
