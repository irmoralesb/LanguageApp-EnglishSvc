import datetime
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.mssql import DATETIME2, UNIQUEIDENTIFIER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.databases.database import Base


class LanguageDataModel(Base):
    __tablename__ = "languages"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_target_language: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_native_language: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class PracticeTermDataModel(Base):
    __tablename__ = "practice_terms"
    __table_args__ = (
        UniqueConstraint("term", "term_type", "created_by_user_id", name="uq_term_type_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    term: Mapped[str] = mapped_column(String(100), nullable=False)
    term_type: Mapped[str] = mapped_column(String(50), nullable=False)
    definition: Mapped[str] = mapped_column(String(500), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_catalog: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class PhrasalVerbDataModel(Base):
    __tablename__ = "phrasal_verbs"
    __table_args__ = (
        UniqueConstraint("verb", "particle", "created_by_user_id", name="uq_verb_particle_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    verb: Mapped[str] = mapped_column(String(100), nullable=False)
    particle: Mapped[str] = mapped_column(String(50), nullable=False)
    definition: Mapped[str] = mapped_column(String(500), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_catalog: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class UserProfileDataModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, unique=True
    )
    native_language_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("languages.id"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    native_language = relationship("LanguageDataModel", lazy="joined")
    learning_languages = relationship(
        "UserLearningLanguageDataModel", back_populates="profile", lazy="joined"
    )
    practice_term_selections = relationship(
        "UserPracticeTermSelectionDataModel", back_populates="profile", lazy="selectin"
    )
    phrasal_verb_selections = relationship(
        "UserPhrasalVerbSelectionDataModel", back_populates="profile", lazy="selectin"
    )
    english_expression_selections = relationship(
        "UserEnglishExpressionSelectionDataModel", back_populates="profile", lazy="selectin"
    )


class UserLearningLanguageDataModel(Base):
    __tablename__ = "user_learning_languages"
    __table_args__ = (
        UniqueConstraint("user_id", "language_id", name="uq_user_learning_language"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False
    )
    language_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("languages.id"), nullable=False
    )

    profile = relationship("UserProfileDataModel", back_populates="learning_languages")
    language = relationship("LanguageDataModel", lazy="joined")


class UserPracticeTermSelectionDataModel(Base):
    __tablename__ = "user_practice_term_selections"
    __table_args__ = (
        UniqueConstraint("user_id", "practice_term_id", name="uq_user_practice_term"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False
    )
    practice_term_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("practice_terms.id"), nullable=False
    )
    added_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    profile = relationship("UserProfileDataModel", back_populates="practice_term_selections")
    practice_term = relationship("PracticeTermDataModel", lazy="joined")


class UserPhrasalVerbSelectionDataModel(Base):
    __tablename__ = "user_phrasal_verb_selections"
    __table_args__ = (
        UniqueConstraint("user_id", "phrasal_verb_id", name="uq_user_phrasal_verb"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False
    )
    phrasal_verb_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("phrasal_verbs.id"), nullable=False
    )
    added_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    profile = relationship("UserProfileDataModel", back_populates="phrasal_verb_selections")
    phrasal_verb = relationship("PhrasalVerbDataModel", lazy="joined")


class PrepositionExerciseResultDataModel(Base):
    __tablename__ = "preposition_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    practice_term_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("practice_terms.id"), nullable=False
    )
    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_target: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    practice_term = relationship("PracticeTermDataModel", lazy="joined")


class PhrasalVerbExerciseResultDataModel(Base):
    __tablename__ = "phrasal_verb_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    phrasal_verb_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("phrasal_verbs.id"), nullable=False
    )
    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_target: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    phrasal_verb = relationship("PhrasalVerbDataModel", lazy="joined")


class MultiplePrepositionsExerciseResultDataModel(Base):
    __tablename__ = "multiple_prepositions_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    sentence_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_target: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    revealed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    terms = relationship(
        "MultiplePrepositionsExerciseResultTermDataModel",
        back_populates="result",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class MultiplePrepositionsExerciseResultTermDataModel(Base):
    __tablename__ = "multiple_prepositions_exercise_result_terms"

    result_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("multiple_prepositions_exercise_results.id", ondelete="CASCADE"),
        primary_key=True,
    )
    practice_term_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("practice_terms.id"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    result = relationship("MultiplePrepositionsExerciseResultDataModel", back_populates="terms")
    practice_term = relationship("PracticeTermDataModel", lazy="joined")


class EnglishExpressionDataModel(Base):
    __tablename__ = "english_expressions"
    __table_args__ = (
        UniqueConstraint("text", "expression_type", "created_by_user_id", name="uq_expression_type_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    expression_type: Mapped[str] = mapped_column(String(30), nullable=False)
    definition: Mapped[str] = mapped_column(String(500), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    register: Mapped[str] = mapped_column(String(20), nullable=False, default="neutral")
    is_catalog: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class UserEnglishExpressionSelectionDataModel(Base):
    __tablename__ = "user_english_expression_selections"
    __table_args__ = (
        UniqueConstraint("user_id", "english_expression_id", name="uq_user_english_expression"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False
    )
    english_expression_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("english_expressions.id"), nullable=False
    )
    added_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    profile = relationship("UserProfileDataModel", back_populates="english_expression_selections")
    english_expression = relationship("EnglishExpressionDataModel", lazy="joined")


class ConfusableWordExerciseResultDataModel(Base):
    __tablename__ = "confusable_word_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    option_a: Mapped[str] = mapped_column(String(50), nullable=False)
    option_b: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_with_blank: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_complete: Mapped[str] = mapped_column(Text, nullable=False)
    correct_word: Mapped[str] = mapped_column(String(50), nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class NaturalRewriteExerciseResultDataModel(Base):
    __tablename__ = "natural_rewrite_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    stiff_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    model_answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class RegisterSwitchExerciseResultDataModel(Base):
    __tablename__ = "register_switch_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    source_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    source_register: Mapped[str] = mapped_column(String(20), nullable=False)
    target_register: Mapped[str] = mapped_column(String(20), nullable=False)
    slang_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    model_answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class EnglishExpressionExerciseResultDataModel(Base):
    __tablename__ = "english_expression_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    english_expression_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("english_expressions.id"), nullable=False
    )
    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_native: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    english_expression = relationship("EnglishExpressionDataModel", lazy="joined")


class PrepositionChoiceExerciseResultDataModel(Base):
    __tablename__ = "preposition_choice_exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    option_a: Mapped[str] = mapped_column(String(50), nullable=False)
    option_b: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_with_blank: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_complete: Mapped[str] = mapped_column(Text, nullable=False)
    correct_preposition: Mapped[str] = mapped_column(String(50), nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )


class ChatSessionDataModel(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True
    )
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    messages = relationship(
        "ChatMessageDataModel",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ChatMessageDataModel.created_at",
    )


class ChatMessageDataModel(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    session = relationship("ChatSessionDataModel", back_populates="messages")
    feedback = relationship(
        "MessageFeedbackDataModel",
        back_populates="message",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class MessageFeedbackDataModel(Base):
    __tablename__ = "message_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    corrections: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    recommendations: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False
    )

    message = relationship("ChatMessageDataModel", back_populates="feedback")
