from abc import ABC, abstractmethod

from domain.entities.chat_message_model import ChatMessageModel
from domain.entities.exercise_model import ExercisePrompt, ExerciseEvaluation
from domain.entities.message_feedback_model import MessageFeedbackModel
from domain.entities.multiple_prepositions_exercise_model import (
    MultiplePrepositionsExercisePrompt,
    MultiplePrepositionsEvaluation,
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


class LLMProviderInterface(ABC):

    @abstractmethod
    async def generate_exercise(
        self,
        practice_term: str,
        term_type: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> ExercisePrompt:
        """Generate an exercise scenario, native sentence, and target-language example."""
        ...

    @abstractmethod
    async def evaluate_answer(
        self,
        practice_term: str,
        term_type: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> ExerciseEvaluation:
        """Evaluate the user's written answer against the expected usage."""
        ...

    @abstractmethod
    async def generate_multiple_prepositions_exercise(
        self,
        practice_terms: list[str],
        native_language: str,
        target_language: str,
    ) -> MultiplePrepositionsExercisePrompt:
        """Generate a native-language sentence whose translation requires using
        all provided prepositions (>=2), plus a reference target-language sentence."""
        ...

    @abstractmethod
    async def evaluate_multiple_prepositions(
        self,
        practice_terms: list[str],
        target_language: str,
        sentence_native: str,
        sentence_target: str,
        user_answer: str,
        attempt_number: int,
    ) -> MultiplePrepositionsEvaluation:
        """Evaluate the user's translation, focusing primarily on correct preposition usage.

        IMPORTANT: the LLM must NOT include the correct sentence in `feedback`. The
        application service controls whether to reveal `correct_sentence_target` to
        the client based on attempt_number.
        """
        ...

    @abstractmethod
    async def generate_preposition_choice_exercise(
        self,
        option_a: str,
        option_b: str,
        native_language: str,
        target_language: str,
    ) -> PrepositionChoiceExercisePrompt:
        """Generate a fill-in-the-blank sentence choosing between two similar prepositions."""
        ...

    @abstractmethod
    async def explain_preposition_choice_mistake(
        self,
        option_a: str,
        option_b: str,
        sentence_with_blank: str,
        user_answer: str,
        correct_preposition: str,
        target_language: str,
    ) -> str:
        """Return short feedback when the learner picked the wrong preposition."""
        ...

    @abstractmethod
    async def generate_phrasal_verb_exercise(
        self,
        phrasal_verb: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> PhrasalVerbExercisePrompt:
        """Generate a phrasal-verb writing exercise."""
        ...

    @abstractmethod
    async def evaluate_phrasal_verb_answer(
        self,
        phrasal_verb: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> PhrasalVerbExerciseEvaluation:
        """Evaluate a phrasal-verb learner answer."""
        ...

    @abstractmethod
    async def get_chat_reply(
        self,
        history: list[ChatMessageModel],
        user_message: str,
    ) -> str:
        """Generate conversational assistant reply for chat practice."""
        ...

    @abstractmethod
    async def analyze_message(self, user_message: str) -> MessageFeedbackModel:
        """Return grammar/style feedback for a single user message."""
        ...
