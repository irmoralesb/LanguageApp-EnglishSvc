from uuid import UUID

from domain.entities.natural_rewrite_exercise_model import (
    NaturalRewriteEvaluation,
    NaturalRewriteExercisePrompt,
    NaturalRewriteHistoryRecord,
)
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.natural_rewrite_exercise_repository import (
    NaturalRewriteExerciseRepositoryInterface,
)
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)


class NaturalRewriteExerciseService:

    def __init__(
        self,
        exercise_repo: NaturalRewriteExerciseRepositoryInterface,
        user_profile_repo: UserProfileRepositoryInterface,
        language_repo: LanguageRepositoryInterface,
        llm_provider: LLMProviderInterface,
        prompt_token_svc: PromptTokenService,
    ):
        self.exercise_repo = exercise_repo
        self.user_profile_repo = user_profile_repo
        self.language_repo = language_repo
        self.llm = llm_provider
        self.prompt_token_svc = prompt_token_svc

    async def generate(
        self,
        user_id: UUID,
        target_language_code: str,
    ) -> tuple[NaturalRewriteExercisePrompt, str]:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        prompt = await self.llm.generate_natural_rewrite(
            native_language=native_lang.name,
            target_language=target_language_code,
        )
        prompt.target_language_code = target_language_code

        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "target_language_code": target_language_code,
                "scenario_native": prompt.scenario_native,
                "stiff_sentence": prompt.stiff_sentence,
                "context_note": prompt.context_note,
            }
        )
        return prompt, token

    async def evaluate(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
    ) -> NaturalRewriteEvaluation:
        try:
            payload = self.prompt_token_svc.verify(prompt_token)
        except InvalidPromptToken as exc:
            raise ExerciseGenerationError(f"Invalid or expired exercise token: {exc}")

        if payload.get("user_id") != str(user_id):
            raise ExerciseGenerationError("Exercise token does not belong to this user.")

        target_language_code = str(payload.get("target_language_code") or "")
        scenario_native = str(payload.get("scenario_native") or "")
        stiff_sentence = str(payload.get("stiff_sentence") or "")

        if not stiff_sentence or not target_language_code:
            raise ExerciseGenerationError("Exercise token is missing required fields.")

        evaluation = await self.llm.evaluate_natural_rewrite(
            scenario_native=scenario_native,
            stiff_sentence=stiff_sentence,
            user_answer=user_answer.strip(),
            target_language=target_language_code,
        )

        model_answer = evaluation.model_answer or stiff_sentence
        record = NaturalRewriteHistoryRecord(
            id=None,
            user_id=user_id,
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            stiff_sentence=stiff_sentence,
            user_answer=user_answer.strip(),
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
            model_answer=model_answer,
        )
        await self.exercise_repo.save_result(record)
        return evaluation

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[NaturalRewriteHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)
