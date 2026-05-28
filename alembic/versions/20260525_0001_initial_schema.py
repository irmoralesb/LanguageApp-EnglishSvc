"""initial unified english schema

Revision ID: 20260525_0001
Revises:
Create Date: 2026-05-25
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision: str = "20260525_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "languages",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_target_language", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_native_language", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("code", name="uq_languages_code"),
    )

    op.create_table(
        "practice_terms",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("term", sa.String(length=100), nullable=False),
        sa.Column("term_type", sa.String(length=50), nullable=False),
        sa.Column("definition", sa.String(length=500), nullable=False),
        sa.Column("example_sentence", sa.String(length=1000), nullable=True),
        sa.Column("is_catalog", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.UniqueConstraint("term", "term_type", "created_by_user_id", name="uq_term_type_user"),
    )

    op.create_table(
        "phrasal_verbs",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("verb", sa.String(length=100), nullable=False),
        sa.Column("particle", sa.String(length=50), nullable=False),
        sa.Column("definition", sa.String(length=500), nullable=False),
        sa.Column("example_sentence", sa.String(length=1000), nullable=True),
        sa.Column("is_catalog", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.UniqueConstraint("verb", "particle", "created_by_user_id", name="uq_verb_particle_user"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("native_language_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("languages.id"), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.Column("updated_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
    )

    op.create_table(
        "user_learning_languages",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("user_profiles.user_id"), nullable=False),
        sa.Column("language_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("languages.id"), nullable=False),
        sa.UniqueConstraint("user_id", "language_id", name="uq_user_learning_language"),
    )

    op.create_table(
        "user_practice_term_selections",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("user_profiles.user_id"), nullable=False),
        sa.Column("practice_term_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("practice_terms.id"), nullable=False),
        sa.Column("added_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.UniqueConstraint("user_id", "practice_term_id", name="uq_user_practice_term"),
    )

    op.create_table(
        "user_phrasal_verb_selections",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("user_profiles.user_id"), nullable=False),
        sa.Column("phrasal_verb_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("phrasal_verbs.id"), nullable=False),
        sa.Column("added_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.UniqueConstraint("user_id", "phrasal_verb_id", name="uq_user_phrasal_verb"),
    )

    op.create_table(
        "preposition_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("practice_term_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("practice_terms.id"), nullable=False),
        sa.Column("exercise_type", sa.String(length=50), nullable=False),
        sa.Column("target_language_code", sa.String(length=10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("sentence_native", sa.Text(), nullable=False),
        sa.Column("sentence_target", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )
    op.create_index("ix_preposition_exercise_results_user_id", "preposition_exercise_results", ["user_id"])

    op.create_table(
        "phrasal_verb_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("phrasal_verb_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("phrasal_verbs.id"), nullable=False),
        sa.Column("exercise_type", sa.String(length=50), nullable=False),
        sa.Column("target_language_code", sa.String(length=10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("sentence_native", sa.Text(), nullable=False),
        sa.Column("sentence_target", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )
    op.create_index("ix_phrasal_verb_exercise_results_user_id", "phrasal_verb_exercise_results", ["user_id"])

    op.create_table(
        "multiple_prepositions_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("target_language_code", sa.String(length=10), nullable=False),
        sa.Column("sentence_native", sa.Text(), nullable=False),
        sa.Column("sentence_target", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("revealed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )
    op.create_index(
        "ix_multiple_prepositions_exercise_results_user_id",
        "multiple_prepositions_exercise_results",
        ["user_id"],
    )

    op.create_table(
        "multiple_prepositions_exercise_result_terms",
        sa.Column(
            "result_id",
            mssql.UNIQUEIDENTIFIER(as_uuid=True),
            sa.ForeignKey("multiple_prepositions_exercise_results.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "practice_term_id",
            mssql.UNIQUEIDENTIFIER(as_uuid=True),
            sa.ForeignKey("practice_terms.id"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
        sa.Column("updated_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            mssql.UNIQUEIDENTIFIER(as_uuid=True),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    op.create_table(
        "message_feedback",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "message_id",
            mssql.UNIQUEIDENTIFIER(as_uuid=True),
            sa.ForeignKey("chat_messages.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("corrections", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("recommendations", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", mssql.DATETIME2(precision=6), nullable=False, server_default=sa.text("sysutcdatetime()")),
    )

    language_table = sa.table(
        "languages",
        sa.column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("is_target_language", sa.Boolean),
        sa.column("is_native_language", sa.Boolean),
    )
    op.bulk_insert(
        language_table,
        [
            {"id": uuid.uuid4(), "code": "en", "name": "English", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "es", "name": "Spanish", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "fr", "name": "French", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "de", "name": "German", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "it", "name": "Italian", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "pt", "name": "Portuguese", "is_target_language": True, "is_native_language": True},
            {"id": uuid.uuid4(), "code": "ja", "name": "Japanese", "is_target_language": True, "is_native_language": False},
        ],
    )

    phrasal_table = sa.table(
        "phrasal_verbs",
        sa.column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("verb", sa.String),
        sa.column("particle", sa.String),
        sa.column("definition", sa.String),
        sa.column("example_sentence", sa.String),
        sa.column("is_catalog", sa.Boolean),
        sa.column("created_by_user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True)),
    )
    op.bulk_insert(
        phrasal_table,
        [
            {
                "id": uuid.uuid4(),
                "verb": "look",
                "particle": "up",
                "definition": "search for information",
                "example_sentence": "I need to look up this word in the dictionary.",
                "is_catalog": True,
                "created_by_user_id": None,
            },
            {
                "id": uuid.uuid4(),
                "verb": "give",
                "particle": "up",
                "definition": "stop doing something",
                "example_sentence": "He decided to give up smoking.",
                "is_catalog": True,
                "created_by_user_id": None,
            },
            {
                "id": uuid.uuid4(),
                "verb": "turn",
                "particle": "on",
                "definition": "activate something",
                "example_sentence": "Please turn on the lights.",
                "is_catalog": True,
                "created_by_user_id": None,
            },
            {
                "id": uuid.uuid4(),
                "verb": "run",
                "particle": "into",
                "definition": "meet unexpectedly",
                "example_sentence": "I ran into an old friend yesterday.",
                "is_catalog": True,
                "created_by_user_id": None,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("message_feedback")
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
    op.drop_table("multiple_prepositions_exercise_result_terms")
    op.drop_index(
        "ix_multiple_prepositions_exercise_results_user_id",
        table_name="multiple_prepositions_exercise_results",
    )
    op.drop_table("multiple_prepositions_exercise_results")
    op.drop_index("ix_phrasal_verb_exercise_results_user_id", table_name="phrasal_verb_exercise_results")
    op.drop_table("phrasal_verb_exercise_results")
    op.drop_index("ix_preposition_exercise_results_user_id", table_name="preposition_exercise_results")
    op.drop_table("preposition_exercise_results")
    op.drop_table("user_phrasal_verb_selections")
    op.drop_table("user_practice_term_selections")
    op.drop_table("user_learning_languages")
    op.drop_table("user_profiles")
    op.drop_table("phrasal_verbs")
    op.drop_table("practice_terms")
    op.drop_table("languages")
