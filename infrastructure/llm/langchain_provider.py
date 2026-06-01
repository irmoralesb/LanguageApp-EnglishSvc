import logging
import uuid
from datetime import datetime
from typing import List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from domain.entities.chat_message_model import ChatMessageModel
from domain.entities.exercise_model import ExerciseEvaluation, ExercisePrompt
from domain.entities.message_feedback_model import (
    CorrectionItem,
    MessageFeedbackModel,
    RecommendationItem,
)
from domain.entities.multiple_prepositions_exercise_model import (
    MultiplePrepositionsEvaluation,
    MultiplePrepositionsExercisePrompt,
)
from domain.entities.preposition_choice_exercise_model import (
    PrepositionChoiceExercisePrompt,
)
from domain.entities.phrasal_verb_exercise_model import (
    ExerciseEvaluation as PhrasalVerbExerciseEvaluation,
)
from domain.entities.phrasal_verb_exercise_model import (
    ExercisePrompt as PhrasalVerbExercisePrompt,
)
from domain.exceptions.chat_errors import ChatLLMError
from domain.exceptions.exercise_errors import LLMProviderError
from domain.interfaces.llm_provider import LLMProviderInterface
from infrastructure.llm.chat_prompts import (
    CONVERSATION_SYSTEM,
    FEEDBACK_SYSTEM,
    build_feedback_prompt,
)
from infrastructure.llm.phrasal_verbs_prompts import (
    EXERCISE_EVALUATION_SYSTEM as PHRASAL_EVALUATION_SYSTEM,
)
from infrastructure.llm.phrasal_verbs_prompts import (
    EXERCISE_GENERATION_SYSTEM as PHRASAL_GENERATION_SYSTEM,
)
from infrastructure.llm.phrasal_verbs_prompts import (
    build_evaluation_prompt as build_phrasal_evaluation_prompt,
)
from infrastructure.llm.phrasal_verbs_prompts import (
    build_exercise_prompt as build_phrasal_generation_prompt,
)
from infrastructure.llm.prompts import (
    EXERCISE_EVALUATION_SYSTEM,
    EXERCISE_GENERATION_SYSTEM,
    MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM,
    MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM,
    build_evaluation_prompt,
    build_exercise_prompt,
    build_multiple_prepositions_evaluation_prompt,
    build_multiple_prepositions_generation_prompt,
)
from infrastructure.llm.prompts.preposition_choice import (
    PREPOSITION_CHOICE_FEEDBACK_SYSTEM,
    PREPOSITION_CHOICE_GENERATION_SYSTEM,
    build_preposition_choice_feedback_prompt,
    build_preposition_choice_generation_prompt,
)

logger = logging.getLogger(__name__)


class _ExerciseOutput(BaseModel):
    scenario_native: str
    sentence_native: str
    sentence_target: str


class _EvaluationOutput(BaseModel):
    is_correct: bool
    feedback: str
    correct_example: Optional[str] = None


class _MultiplePrepositionsOutput(BaseModel):
    sentence_native: str
    sentence_target: str
    used_prepositions: List[str] = Field(default_factory=list)


class _PrepositionFeedbackItem(BaseModel):
    preposition: str
    used_correctly: bool
    explanation: str


class _MultiplePrepositionsEvalOutput(BaseModel):
    is_correct: bool
    feedback: str
    preposition_feedback: List[_PrepositionFeedbackItem] = Field(default_factory=list)
    minor_issues: List[str] = Field(default_factory=list)


class _PrepositionChoiceOutput(BaseModel):
    scenario_native: str = ""
    sentence_with_blank: str
    correct_preposition: str
    sentence_complete: str


class _PrepositionChoiceFeedbackOutput(BaseModel):
    feedback: str


class _CorrectionOutput(BaseModel):
    original: str
    issue: str
    suggestion: str


class _RecommendationOutput(BaseModel):
    original: str
    better_expression: str
    reason: str


class _FeedbackOutput(BaseModel):
    corrections: list[_CorrectionOutput] = []
    recommendations: list[_RecommendationOutput] = []


class LangChainProvider(LLMProviderInterface):
    """
    LLM provider backed by LangChain's init_chat_model.

    Supports any provider that has a langchain-<provider> integration package
    installed (e.g. openai, anthropic, google-genai, mistralai).
    """

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> None:
        self._provider = provider
        try:
            llm = init_chat_model(
                model=model,
                model_provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
        except ImportError as exc:
            raise LLMProviderError(
                provider,
                f"Missing integration package for provider '{provider}'. "
                f"Install 'langchain-{provider}' and add it to requirements.txt. "
                f"Original error: {exc}",
            )

        self._exercise_chain = llm.with_structured_output(_ExerciseOutput)
        self._eval_chain = llm.with_structured_output(_EvaluationOutput)
        self._multi_prep_chain = llm.with_structured_output(_MultiplePrepositionsOutput)
        self._multi_prep_eval_chain = llm.with_structured_output(
            _MultiplePrepositionsEvalOutput
        )
        self._preposition_choice_chain = llm.with_structured_output(_PrepositionChoiceOutput)
        self._preposition_choice_feedback_chain = llm.with_structured_output(
            _PrepositionChoiceFeedbackOutput
        )
        self._phrasal_exercise_chain = llm.with_structured_output(_ExerciseOutput)
        self._phrasal_eval_chain = llm.with_structured_output(_EvaluationOutput)
        self._conversation_llm = llm
        self._feedback_chain = llm.with_structured_output(_FeedbackOutput)

    async def generate_exercise(
        self,
        practice_term: str,
        term_type: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> ExercisePrompt:
        user_msg = build_exercise_prompt(
            practice_term=practice_term,
            term_type=term_type,
            definition=definition,
            native_language=native_language,
            target_language=target_language,
            situation=situation,
        )
        messages = [
            SystemMessage(content=EXERCISE_GENERATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _ExerciseOutput = await self._exercise_chain.ainvoke(messages)
            return ExercisePrompt(
                practice_term_id=None,
                practice_term_text=practice_term,
                term_type=term_type,
                target_language_code="",
                scenario_native=result.scenario_native,
                sentence_native=result.sentence_native,
                sentence_target=result.sentence_target,
            )
        except Exception as exc:
            logger.error(
                "Exercise generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def evaluate_answer(
        self,
        practice_term: str,
        term_type: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> ExerciseEvaluation:
        user_msg = build_evaluation_prompt(
            practice_term=practice_term,
            term_type=term_type,
            target_language=target_language,
            sentence_target=sentence_target,
            user_answer=user_answer,
        )
        messages = [
            SystemMessage(content=EXERCISE_EVALUATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _EvaluationOutput = await self._eval_chain.ainvoke(messages)
            return ExerciseEvaluation(
                is_correct=result.is_correct,
                feedback=result.feedback,
                correct_example=result.correct_example,
            )
        except Exception as exc:
            logger.error(
                "Answer evaluation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def generate_multiple_prepositions_exercise(
        self,
        practice_terms: list[str],
        native_language: str,
        target_language: str,
    ) -> MultiplePrepositionsExercisePrompt:
        user_msg = build_multiple_prepositions_generation_prompt(
            prepositions=practice_terms,
            native_language=native_language,
            target_language=target_language,
        )
        messages = [
            SystemMessage(content=MULTIPLE_PREPOSITIONS_GENERATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _MultiplePrepositionsOutput = await self._multi_prep_chain.ainvoke(messages)
            return MultiplePrepositionsExercisePrompt(
                practice_term_ids=[],
                practice_term_texts=list(practice_terms),
                target_language_code=target_language,
                sentence_native=result.sentence_native,
                sentence_target=result.sentence_target,
            )
        except Exception as exc:
            logger.error(
                "Multiple-prepositions exercise generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def evaluate_multiple_prepositions(
        self,
        practice_terms: list[str],
        target_language: str,
        sentence_native: str,
        sentence_target: str,
        user_answer: str,
        attempt_number: int,
    ) -> MultiplePrepositionsEvaluation:
        user_msg = build_multiple_prepositions_evaluation_prompt(
            prepositions=practice_terms,
            native_language_or_source="the learner's native language",
            target_language=target_language,
            sentence_native=sentence_native,
            sentence_target=sentence_target,
            user_answer=user_answer,
        )
        messages = [
            SystemMessage(content=MULTIPLE_PREPOSITIONS_EVALUATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _MultiplePrepositionsEvalOutput = await self._multi_prep_eval_chain.ainvoke(messages)
            return MultiplePrepositionsEvaluation(
                is_correct=result.is_correct,
                feedback=result.feedback,
                preposition_feedback=[item.model_dump() for item in result.preposition_feedback],
                minor_issues=list(result.minor_issues),
                correct_sentence_target=None,
            )
        except Exception as exc:
            logger.error(
                "Multiple-prepositions evaluation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def generate_preposition_choice_exercise(
        self,
        option_a: str,
        option_b: str,
        native_language: str,
        target_language: str,
    ) -> PrepositionChoiceExercisePrompt:
        user_msg = build_preposition_choice_generation_prompt(
            option_a=option_a,
            option_b=option_b,
            native_language=native_language,
            target_language=target_language,
        )
        messages = [
            SystemMessage(content=PREPOSITION_CHOICE_GENERATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _PrepositionChoiceOutput = await self._preposition_choice_chain.ainvoke(
                messages
            )
            return PrepositionChoiceExercisePrompt(
                option_a=option_a,
                option_b=option_b,
                target_language_code=target_language,
                scenario_native=result.scenario_native,
                sentence_with_blank=result.sentence_with_blank,
                correct_preposition=result.correct_preposition.strip().lower(),
                sentence_complete=result.sentence_complete,
            )
        except Exception as exc:
            logger.error(
                "Preposition choice exercise generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def explain_preposition_choice_mistake(
        self,
        option_a: str,
        option_b: str,
        sentence_with_blank: str,
        user_answer: str,
        correct_preposition: str,
        target_language: str,
    ) -> str:
        user_msg = build_preposition_choice_feedback_prompt(
            option_a=option_a,
            option_b=option_b,
            sentence_with_blank=sentence_with_blank,
            user_answer=user_answer,
            correct_preposition=correct_preposition,
            target_language=target_language,
        )
        messages = [
            SystemMessage(content=PREPOSITION_CHOICE_FEEDBACK_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _PrepositionChoiceFeedbackOutput = (
                await self._preposition_choice_feedback_chain.ainvoke(messages)
            )
            return result.feedback
        except Exception as exc:
            logger.error(
                "Preposition choice feedback failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def generate_phrasal_verb_exercise(
        self,
        phrasal_verb: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> PhrasalVerbExercisePrompt:
        user_msg = build_phrasal_generation_prompt(
            phrasal_verb=phrasal_verb,
            definition=definition,
            native_language=native_language,
            target_language=target_language,
            situation=situation,
        )
        messages = [
            SystemMessage(content=PHRASAL_GENERATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _ExerciseOutput = await self._phrasal_exercise_chain.ainvoke(messages)
            return PhrasalVerbExercisePrompt(
                phrasal_verb_id=None,
                phrasal_verb_text=phrasal_verb,
                target_language_code="",
                scenario_native=result.scenario_native,
                sentence_native=result.sentence_native,
                sentence_target=result.sentence_target,
            )
        except Exception as exc:
            logger.error(
                "Phrasal verb exercise generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def evaluate_phrasal_verb_answer(
        self,
        phrasal_verb: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> PhrasalVerbExerciseEvaluation:
        user_msg = build_phrasal_evaluation_prompt(
            phrasal_verb=phrasal_verb,
            target_language=target_language,
            sentence_target=sentence_target,
            user_answer=user_answer,
        )
        messages = [
            SystemMessage(content=PHRASAL_EVALUATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _EvaluationOutput = await self._phrasal_eval_chain.ainvoke(messages)
            return PhrasalVerbExerciseEvaluation(
                is_correct=result.is_correct,
                feedback=result.feedback,
                correct_example=result.correct_example,
            )
        except Exception as exc:
            logger.error(
                "Phrasal verb evaluation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def get_chat_reply(
        self,
        history: list[ChatMessageModel],
        user_message: str,
    ) -> str:
        messages = [SystemMessage(content=CONVERSATION_SYSTEM)]
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        messages.append(HumanMessage(content=user_message))
        try:
            result = await self._conversation_llm.ainvoke(messages)
            return result.content
        except Exception as exc:
            logger.error(
                "Chat reply generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise ChatLLMError(self._provider, str(exc))

    async def analyze_message(
        self,
        user_message: str,
    ) -> MessageFeedbackModel:
        messages = [
            SystemMessage(content=FEEDBACK_SYSTEM),
            HumanMessage(content=build_feedback_prompt(user_message)),
        ]
        try:
            result: _FeedbackOutput = await self._feedback_chain.ainvoke(messages)
            corrections = [
                CorrectionItem(
                    original=c.original,
                    issue=c.issue,
                    suggestion=c.suggestion,
                )
                for c in result.corrections
            ]
            recommendations = [
                RecommendationItem(
                    original=r.original,
                    better_expression=r.better_expression,
                    reason=r.reason,
                )
                for r in result.recommendations
            ]
            return MessageFeedbackModel(
                id=uuid.uuid4(),
                message_id=uuid.uuid4(),
                corrections=corrections,
                recommendations=recommendations,
                created_at=datetime.utcnow(),
            )
        except Exception as exc:
            logger.error(
                "Message analysis failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise ChatLLMError(self._provider, str(exc))
