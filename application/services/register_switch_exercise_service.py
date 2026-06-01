import random as rand_mod
from uuid import UUID

from domain.entities.english_expression_model import REGISTERS
from domain.entities.register_switch_exercise_model import (
    RegisterSwitchEvaluation,
    RegisterSwitchExercisePrompt,
    RegisterSwitchHistoryRecord,
)
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.register_switch_exercise_repository import (
    RegisterSwitchExerciseRepositoryInterface,
)
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)

_SLANG_LEVELS = ("light", "moderate", "heavy")


class RegisterSwitchExerciseService:

    def __init__(
        self,
        exercise_repo: RegisterSwitchExerciseRepositoryInterface,
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

    @staticmethod
    def _pick_registers() -> tuple[str, str]:
        source, target = rand_mod.sample(list(REGISTERS), 2)
        return source, target

    async def generate(
        self,
        user_id: UUID,
        target_language_code: str,
        target_register: str | None = None,
        slang_level: str | None = None,
    ) -> tuple[RegisterSwitchExercisePrompt, str]:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        source_register, resolved_target = self._pick_registers()
        if target_register is not None:
            resolved_target = target_register.strip().lower()
            if resolved_target not in REGISTERS:
                raise ExerciseGenerationError(
                    f"target_register must be one of: {', '.join(REGISTERS)}",
                )
            if resolved_target == source_register:
                others = [r for r in REGISTERS if r != source_register]
                source_register = rand_mod.choice(others)

        resolved_slang = slang_level
        if resolved_target == "casual" and resolved_slang is None:
            resolved_slang = rand_mod.choice(_SLANG_LEVELS)
        elif resolved_target != "casual":
            resolved_slang = None

        prompt = await self.llm.generate_register_switch(
            native_language=native_lang.name,
            target_language=target_language_code,
            source_register=source_register,
            target_register=resolved_target,
            slang_level=resolved_slang,
        )
        prompt.target_language_code = target_language_code
        prompt.target_register = resolved_target
        prompt.slang_level = resolved_slang

        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "target_language_code": target_language_code,
                "scenario_native": prompt.scenario_native,
                "source_sentence": prompt.source_sentence,
                "source_register": prompt.source_register,
                "target_register": prompt.target_register,
                "slang_level": prompt.slang_level or "",
            }
        )
        return prompt, token

    async def evaluate(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
    ) -> RegisterSwitchEvaluation:
        try:
            payload = self.prompt_token_svc.verify(prompt_token)
        except InvalidPromptToken as exc:
            raise ExerciseGenerationError(f"Invalid or expired exercise token: {exc}")

        if payload.get("user_id") != str(user_id):
            raise ExerciseGenerationError("Exercise token does not belong to this user.")

        target_language_code = str(payload.get("target_language_code") or "")
        scenario_native = str(payload.get("scenario_native") or "")
        source_sentence = str(payload.get("source_sentence") or "")
        source_register = str(payload.get("source_register") or "")
        target_register = str(payload.get("target_register") or "")
        slang_raw = str(payload.get("slang_level") or "")
        slang_level = slang_raw if slang_raw else None

        if not source_sentence or not target_language_code:
            raise ExerciseGenerationError("Exercise token is missing required fields.")

        evaluation = await self.llm.evaluate_register_switch(
            scenario_native=scenario_native,
            source_sentence=source_sentence,
            source_register=source_register,
            target_register=target_register,
            slang_level=slang_level,
            user_answer=user_answer.strip(),
            target_language=target_language_code,
        )

        model_answer = evaluation.model_answer or source_sentence
        record = RegisterSwitchHistoryRecord(
            id=None,
            user_id=user_id,
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            source_sentence=source_sentence,
            source_register=source_register,
            target_register=target_register,
            slang_level=slang_level,
            user_answer=user_answer.strip(),
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
            model_answer=model_answer,
        )
        await self.exercise_repo.save_result(record)
        return evaluation

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[RegisterSwitchHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)
