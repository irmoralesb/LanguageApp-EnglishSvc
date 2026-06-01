"""add preposition choice exercise results table

Revision ID: 20260531_0004
Revises: 20260526_0003
Create Date: 2026-05-31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision: str = "20260531_0004"
down_revision: Union[str, None] = "20260526_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "preposition_choice_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("option_a", sa.String(50), nullable=False),
        sa.Column("option_b", sa.String(50), nullable=False),
        sa.Column("target_language_code", sa.String(10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("sentence_with_blank", sa.Text(), nullable=False),
        sa.Column("sentence_complete", sa.Text(), nullable=False),
        sa.Column("correct_preposition", sa.String(50), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            mssql.DATETIME2(precision=6),
            server_default=sa.text("SYSUTCDATETIME()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_preposition_choice_exercise_results_user_id",
        "preposition_choice_exercise_results",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_preposition_choice_exercise_results_user_id",
        table_name="preposition_choice_exercise_results",
    )
    op.drop_table("preposition_choice_exercise_results")
