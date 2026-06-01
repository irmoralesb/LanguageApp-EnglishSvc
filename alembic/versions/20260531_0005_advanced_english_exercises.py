"""Advanced English exercises: confusables, rewrite, register, expressions catalog

Revision ID: 20260531_0005
Revises: 20260531_0004
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision: str = "20260531_0005"
down_revision: Union[str, None] = "20260531_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_IDIOMS = [
    ("break the ice", "Start a conversation in a social setting.", "Let's play a game to break the ice.", "neutral"),
    ("once in a blue moon", "Very rarely.", "We only eat out once in a blue moon.", "neutral"),
    ("hit the nail on the head", "Be exactly right.", "You hit the nail on the head with that summary.", "neutral"),
    ("let the cat out of the bag", "Reveal a secret accidentally.", "Who let the cat out of the bag about the surprise?", "casual"),
    ("under the weather", "Feeling ill.", "I'm a bit under the weather today.", "casual"),
    ("piece of cake", "Very easy.", "The exam was a piece of cake.", "casual"),
    ("spill the beans", "Reveal secret information.", "Don't spill the beans about the party.", "casual"),
    ("cost an arm and a leg", "Be very expensive.", "That car costs an arm and a leg.", "casual"),
    ("on cloud nine", "Extremely happy.", "She's been on cloud nine since the promotion.", "neutral"),
    ("burn the midnight oil", "Work late into the night.", "We burned the midnight oil to finish the report.", "formal"),
    ("the ball is in your court", "It's your decision or responsibility.", "I've made my offer; the ball is in your court.", "neutral"),
    ("bite the bullet", "Face a difficult situation bravely.", "We'll have to bite the bullet and cut costs.", "neutral"),
    ("call it a day", "Stop working for the day.", "It's late; let's call it a day.", "casual"),
    ("get cold feet", "Become nervous and hesitate.", "He got cold feet before the presentation.", "casual"),
    ("in hot water", "In trouble.", "He's in hot water with his manager.", "casual"),
    ("jump on the bandwagon", "Join a popular trend.", "Many firms jumped on the AI bandwagon.", "neutral"),
    ("miss the boat", "Miss an opportunity.", "If you wait too long, you'll miss the boat.", "neutral"),
    ("pull someone's leg", "Joke or tease someone.", "Relax, I was just pulling your leg.", "casual"),
    ("see eye to eye", "Agree completely.", "We don't see eye to eye on politics.", "neutral"),
    ("speak of the devil", "Said when someone appears after being mentioned.", "Speak of the devil—we were just talking about you!", "casual"),
]

_COLLOCATIONS = [
    ("make a decision", "decide", "You need to make a decision by Friday.", "neutral"),
    ("heavy rain", "rain", "Heavy rain flooded the streets.", "neutral"),
    ("strong coffee", "coffee", "I prefer strong coffee in the morning.", "neutral"),
    ("fast food", "food", "We grabbed some fast food on the way.", "neutral"),
    ("deep sleep", "sleep", "After the hike I fell into a deep sleep.", "neutral"),
    ("sharp contrast", "contrast", "There is a sharp contrast between the two plans.", "formal"),
    ("commit a crime", "crime", "He was charged with committing a crime.", "formal"),
    ("pay attention", "attention", "Please pay attention to the instructions.", "neutral"),
    ("take a risk", "risk", "Investors must be willing to take a risk.", "neutral"),
    ("do homework", "homework", "The kids need to do their homework.", "neutral"),
    ("make progress", "progress", "The team is making progress on the project.", "neutral"),
    ("catch a cold", "cold", "I think I'm catching a cold.", "casual"),
    ("lose weight", "weight", "She's trying to lose weight safely.", "neutral"),
    ("gain experience", "experience", "Internships help you gain experience.", "formal"),
    ("break a habit", "habit", "It's hard to break a habit.", "neutral"),
    ("raise awareness", "awareness", "The campaign aims to raise awareness.", "formal"),
    ("meet demand", "demand", "Suppliers struggle to meet demand.", "formal"),
    ("run a business", "business", "She runs a business from home.", "neutral"),
    ("set a record", "record", "The athlete set a new record.", "neutral"),
    ("tell the truth", "truth", "Always tell the truth in court.", "formal"),
]


def upgrade() -> None:
    op.create_table(
        "confusable_word_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("option_a", sa.String(50), nullable=False),
        sa.Column("option_b", sa.String(50), nullable=False),
        sa.Column("target_language_code", sa.String(10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("sentence_with_blank", sa.Text(), nullable=False),
        sa.Column("sentence_complete", sa.Text(), nullable=False),
        sa.Column("correct_word", sa.String(50), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
    )
    op.create_index("ix_confusable_word_exercise_results_user_id", "confusable_word_exercise_results", ["user_id"])

    op.create_table(
        "natural_rewrite_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("target_language_code", sa.String(10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("stiff_sentence", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("model_answer", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
    )
    op.create_index("ix_natural_rewrite_exercise_results_user_id", "natural_rewrite_exercise_results", ["user_id"])

    op.create_table(
        "register_switch_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("target_language_code", sa.String(10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("source_sentence", sa.Text(), nullable=False),
        sa.Column("source_register", sa.String(20), nullable=False),
        sa.Column("target_register", sa.String(20), nullable=False),
        sa.Column("slang_level", sa.String(20), nullable=True),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("model_answer", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
    )
    op.create_index("ix_register_switch_exercise_results_user_id", "register_switch_exercise_results", ["user_id"])

    op.create_table(
        "english_expressions",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("text", sa.String(200), nullable=False),
        sa.Column("expression_type", sa.String(30), nullable=False),
        sa.Column("definition", sa.String(500), nullable=False),
        sa.Column("example_sentence", sa.String(1000), nullable=True),
        sa.Column("register", sa.String(20), nullable=False, server_default="neutral"),
        sa.Column("is_catalog", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_by_user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.UniqueConstraint("text", "expression_type", "created_by_user_id", name="uq_expression_type_user"),
    )

    op.create_table(
        "user_english_expression_selections",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("user_profiles.user_id"), nullable=False),
        sa.Column("english_expression_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("english_expressions.id"), nullable=False),
        sa.Column("added_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.UniqueConstraint("user_id", "english_expression_id", name="uq_user_english_expression"),
    )

    op.create_table(
        "english_expression_exercise_results",
        sa.Column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True), primary_key=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), nullable=False),
        sa.Column("english_expression_id", mssql.UNIQUEIDENTIFIER(as_uuid=True), sa.ForeignKey("english_expressions.id"), nullable=False),
        sa.Column("exercise_type", sa.String(50), nullable=False),
        sa.Column("target_language_code", sa.String(10), nullable=False),
        sa.Column("scenario_native", sa.Text(), nullable=False),
        sa.Column("prompt_native", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", mssql.DATETIME2(precision=6), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
    )
    op.create_index("ix_english_expression_exercise_results_user_id", "english_expression_exercise_results", ["user_id"])

    conn = op.get_bind()
    for text, definition, example, register in _IDIOMS:
        conn.execute(
            sa.text(
                "INSERT INTO english_expressions (id, text, expression_type, definition, example_sentence, register, is_catalog) "
                "VALUES (:id, :text, 'idiom', :definition, :example, :register, 1)"
            ),
            {"id": str(uuid.uuid4()), "text": text, "definition": definition, "example": example, "register": register},
        )
    for text, definition, example, register in _COLLOCATIONS:
        conn.execute(
            sa.text(
                "INSERT INTO english_expressions (id, text, expression_type, definition, example_sentence, register, is_catalog) "
                "VALUES (:id, :text, 'collocation', :definition, :example, :register, 1)"
            ),
            {"id": str(uuid.uuid4()), "text": text, "definition": definition, "example": example, "register": register},
        )


def downgrade() -> None:
    op.drop_index("ix_english_expression_exercise_results_user_id", table_name="english_expression_exercise_results")
    op.drop_table("english_expression_exercise_results")
    op.drop_table("user_english_expression_selections")
    op.drop_table("english_expressions")
    op.drop_index("ix_register_switch_exercise_results_user_id", table_name="register_switch_exercise_results")
    op.drop_table("register_switch_exercise_results")
    op.drop_index("ix_natural_rewrite_exercise_results_user_id", table_name="natural_rewrite_exercise_results")
    op.drop_table("natural_rewrite_exercise_results")
    op.drop_index("ix_confusable_word_exercise_results_user_id", table_name="confusable_word_exercise_results")
    op.drop_table("confusable_word_exercise_results")
