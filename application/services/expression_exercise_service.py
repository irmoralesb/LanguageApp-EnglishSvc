import random as rand_mod
import re
from uuid import UUID

from domain.entities.english_expression_model import EnglishExpressionModel
from domain.entities.expression_exercise_model import (
    CollocationChoiceExercisePrompt,
    ExpressionExerciseEvaluation,
    ExpressionExerciseHistoryRecord,
    ExpressionWritingPrompt,
    IdiomCompleteExercisePrompt,
)
from domain.exceptions.english_expression_errors import EnglishExpressionNotFoundError
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.user_profile_errors import UserProfileNotFoundError
from domain.interfaces.english_expression_repository import EnglishExpressionRepositoryInterface
from domain.interfaces.expression_exercise_repository import ExpressionExerciseRepositoryInterface
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from application.services.prompt_token_service import (
    PromptTokenService,
    InvalidPromptToken,
)


def _normalize_answer(value: str) -> str:
    return value.strip().lower()


def _blank_phrase_in_sentence(sentence: str, phrase: str) -> tuple[str, str]:
    sent = sentence.strip()
    text = phrase.strip()
    pattern = re.compile(re.escape(text), re.IGNORECASE)
    match = pattern.search(sent)
    if not match:
        return f"{sent} ___", text
    correct = sent[match.start():match.end()]
    blanked = sent[: match.start()] + "___" + sent[match.end():]
    return blanked, correct


def _blank_first_word(sentence: str, phrase: str) -> tuple[str, str]:
    parts = phrase.strip().split(maxsplit=1)
    if len(parts) < 2:
        return _blank_phrase_in_sentence(sentence, phrase)
    first_word, rest = parts[0], parts[1]
    sent = sentence.strip()
    pattern = re.compile(re.escape(first_word), re.IGNORECASE)
    match = pattern.search(sent)
    if not match:
        return f"{sent} ___ {rest}", first_word
    correct = sent[match.start():match.end()]
    blanked = sent[: match.start()] + "___" + sent[match.end():]
    return blanked, correct


class ExpressionExerciseService:

    def __init__(
        self,
        exercise_repo: ExpressionExerciseRepositoryInterface,
        expression_repo: EnglishExpressionRepositoryInterface,
        user_profile_repo: UserProfileRepositoryInterface,
        language_repo: LanguageRepositoryInterface,
        llm_provider: LLMProviderInterface,
        prompt_token_svc: PromptTokenService,
    ):
        self.exercise_repo = exercise_repo
        self.expression_repo = expression_repo
        self.user_profile_repo = user_profile_repo
        self.language_repo = language_repo
        self.llm = llm_provider
        self.prompt_token_svc = prompt_token_svc

    async def _pick_expression(
        self,
        user_id: UUID,
        expression_type: str,
        english_expression_id: UUID | None = None,
    ) -> EnglishExpressionModel:
        if english_expression_id is not None:
            expr = await self.expression_repo.get_by_id(english_expression_id)
            if expr is None:
                raise EnglishExpressionNotFoundError(english_expression_id)
            if expr.expression_type != expression_type:
                raise ExerciseGenerationError(
                    f"Expression is not of type '{expression_type}'.",
                )
            return expr

        selections = await self.user_profile_repo.get_english_expression_selections(user_id)
        candidates: list[EnglishExpressionModel] = []
        if selections:
            for sel in selections:
                expr = await self.expression_repo.get_by_id(sel.english_expression_id)
                if expr is not None and expr.expression_type == expression_type:
                    candidates.append(expr)
        else:
            candidates = await self.expression_repo.get_catalog(
                skip=0, limit=200, expression_type=expression_type,
            )

        if not candidates:
            raise ExerciseGenerationError(
                f"Select at least one {expression_type} in your profile, or ensure the catalog has items.",
            )
        return rand_mod.choice(candidates)

    async def _distractor_options(
        self,
        correct: str,
        expression_type: str,
        exclude_id: UUID,
    ) -> list[str]:
        catalog = await self.expression_repo.get_catalog(
            skip=0, limit=200, expression_type=expression_type,
        )
        pool: list[str] = []
        for item in catalog:
            if item.id == exclude_id:
                continue
            if expression_type == "collocation":
                word = item.text.strip().split(maxsplit=1)[0]
            else:
                word = item.text.strip()
            if _normalize_answer(word) != _normalize_answer(correct) and word not in pool:
                pool.append(word)
        rand_mod.shuffle(pool)
        options = [correct] + pool[:3]
        while len(options) < 4:
            options.append(f"({len(options)})")
        rand_mod.shuffle(options)
        return options

    async def generate_idiom_complete(
        self,
        user_id: UUID,
        english_expression_id: UUID | None = None,
    ) -> tuple[IdiomCompleteExercisePrompt, str]:
        expr = await self._pick_expression(user_id, "idiom", english_expression_id)
        if not expr.example_sentence:
            raise ExerciseGenerationError(
                f"Idiom '{expr.text}' has no example sentence in the catalog.",
            )

        sentence_with_blank, correct = _blank_phrase_in_sentence(
            expr.example_sentence, expr.text,
        )
        options = await self._distractor_options(correct, "idiom", expr.id)  # type: ignore[arg-type]

        prompt = IdiomCompleteExercisePrompt(
            english_expression_id=expr.id,  # type: ignore[arg-type]
            text=expr.text,
            definition=expr.definition,
            sentence_with_blank=sentence_with_blank,
            options=options,
            scenario_native=expr.definition,
        )
        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "exercise_type": "idiom-complete",
                "english_expression_id": str(expr.id),
                "sentence_with_blank": sentence_with_blank,
                "correct_answer": correct,
                "definition": expr.definition,
            }
        )
        return prompt, token

    async def generate_collocation_choice(
        self,
        user_id: UUID,
        english_expression_id: UUID | None = None,
    ) -> tuple[CollocationChoiceExercisePrompt, str]:
        expr = await self._pick_expression(user_id, "collocation", english_expression_id)
        if not expr.example_sentence:
            raise ExerciseGenerationError(
                f"Collocation '{expr.text}' has no example sentence in the catalog.",
            )

        sentence_with_blank, correct = _blank_first_word(
            expr.example_sentence, expr.text,
        )
        options = await self._distractor_options(correct, "collocation", expr.id)  # type: ignore[arg-type]

        prompt = CollocationChoiceExercisePrompt(
            english_expression_id=expr.id,  # type: ignore[arg-type]
            text=expr.text,
            definition=expr.definition,
            sentence_with_blank=sentence_with_blank,
            options=options,
            scenario_native=expr.definition,
        )
        token = self.prompt_token_svc.sign(
            {
                "user_id": str(user_id),
                "exercise_type": "collocation-choice",
                "english_expression_id": str(expr.id),
                "sentence_with_blank": sentence_with_blank,
                "correct_answer": correct,
                "definition": expr.definition,
            }
        )
        return prompt, token

    async def evaluate_multiple_choice(
        self,
        user_id: UUID,
        prompt_token: str,
        user_answer: str,
    ) -> ExpressionExerciseEvaluation:
        try:
            payload = self.prompt_token_svc.verify(prompt_token)
        except InvalidPromptToken as exc:
            raise ExerciseGenerationError(f"Invalid or expired exercise token: {exc}")

        if payload.get("user_id") != str(user_id):
            raise ExerciseGenerationError("Exercise token does not belong to this user.")

        exercise_type = str(payload.get("exercise_type") or "")
        expression_id = UUID(str(payload.get("english_expression_id")))
        sentence_with_blank = str(payload.get("sentence_with_blank") or "")
        correct_answer = str(payload.get("correct_answer") or "")
        definition = str(payload.get("definition") or "")

        normalized_user = _normalize_answer(user_answer)
        is_correct = normalized_user == _normalize_answer(correct_answer)

        if is_correct:
            feedback = f'Correct! The answer is "{correct_answer}".'
        else:
            feedback = (
                f'Not quite. The correct answer is "{correct_answer}". '
                f"Definition: {definition}"
            )

        await self._save_mc_result(
            user_id=user_id,
            english_expression_id=expression_id,
            exercise_type=exercise_type,
            prompt_native=sentence_with_blank,
            expected_answer=correct_answer,
            user_answer=user_answer,
            is_correct=is_correct,
            feedback=feedback,
            scenario_native=definition,
        )

        return ExpressionExerciseEvaluation(
            is_correct=is_correct,
            feedback=feedback,
            correct_example=None if is_correct else correct_answer,
        )

    async def _save_mc_result(
        self,
        user_id: UUID,
        english_expression_id: UUID,
        exercise_type: str,
        prompt_native: str,
        expected_answer: str,
        user_answer: str,
        is_correct: bool,
        feedback: str,
        scenario_native: str,
    ) -> None:
        record = ExpressionExerciseHistoryRecord(
            id=None,
            user_id=user_id,
            english_expression_id=english_expression_id,
            exercise_type=exercise_type,
            target_language_code="en",
            scenario_native=scenario_native,
            prompt_native=prompt_native,
            expected_answer=expected_answer,
            user_answer=user_answer,
            is_correct=is_correct,
            feedback=feedback,
        )
        await self.exercise_repo.save_result(record)

    async def _pick_idiom_or_collocation(
        self,
        user_id: UUID,
        english_expression_id: UUID | None,
    ) -> EnglishExpressionModel:
        if english_expression_id is not None:
            expr = await self.expression_repo.get_by_id(english_expression_id)
            if expr is None:
                raise EnglishExpressionNotFoundError(english_expression_id)
            if expr.expression_type not in ("idiom", "collocation"):
                raise ExerciseGenerationError(
                    "use-in-context supports idioms and collocations only.",
                )
            return expr

        for expr_type in ("idiom", "collocation"):
            try:
                return await self._pick_expression(user_id, expr_type, None)
            except ExerciseGenerationError:
                continue
        raise ExerciseGenerationError(
            "Select at least one idiom or collocation in your profile.",
        )

    async def generate_use_in_context(
        self,
        user_id: UUID,
        target_language_code: str,
        english_expression_id: UUID | None = None,
    ) -> ExpressionWritingPrompt:
        expr = await self._pick_idiom_or_collocation(user_id, english_expression_id)

        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        llm_prompt = await self.llm.generate_exercise(
            practice_term=expr.text,
            term_type=expr.expression_type,
            definition=expr.definition,
            native_language=native_lang.name,
            target_language=target_language_code,
        )

        return ExpressionWritingPrompt(
            english_expression_id=expr.id,  # type: ignore[arg-type]
            text=expr.text,
            expression_type=expr.expression_type,
            definition=expr.definition,
            target_language_code=target_language_code,
            scenario_native=llm_prompt.scenario_native,
            prompt_native=llm_prompt.sentence_native,
            expected_answer=llm_prompt.sentence_target,
        )

    async def evaluate_use_in_context(
        self,
        user_id: UUID,
        english_expression_id: UUID,
        target_language_code: str,
        scenario_native: str,
        prompt_native: str,
        expected_answer: str,
        user_answer: str,
    ) -> ExpressionExerciseEvaluation:
        expr = await self.expression_repo.get_by_id(english_expression_id)
        if expr is None:
            raise EnglishExpressionNotFoundError(english_expression_id)

        evaluation = await self.llm.evaluate_answer(
            practice_term=expr.text,
            term_type=expr.expression_type,
            target_language=target_language_code,
            sentence_target=expected_answer,
            user_answer=user_answer,
        )

        record = ExpressionExerciseHistoryRecord(
            id=None,
            user_id=user_id,
            english_expression_id=english_expression_id,
            exercise_type="use-in-context",
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            prompt_native=prompt_native,
            expected_answer=expected_answer,
            user_answer=user_answer,
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
        )
        await self.exercise_repo.save_result(record)

        return ExpressionExerciseEvaluation(
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
            correct_example=evaluation.correct_example,
        )

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExpressionExerciseHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)
