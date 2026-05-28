"""seed practice terms catalog (5 prepositions matching PrepositionsSvc)

Revision ID: 20260526_0003
Revises: 20260526_0002
Create Date: 2026-05-26
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision: str = "20260526_0003"
down_revision: Union[str, None] = "20260526_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    practice_terms_table = sa.table(
        "practice_terms",
        sa.column("id", mssql.UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("term", sa.String),
        sa.column("term_type", sa.String),
        sa.column("definition", sa.String),
        sa.column("example_sentence", sa.String),
        sa.column("is_catalog", sa.Boolean),
        sa.column("created_by_user_id", mssql.UNIQUEIDENTIFIER(as_uuid=True)),
    )

    def _row(n: int, term: str, term_type: str, definition: str, example: str) -> dict:
        return {
            "id": uuid.UUID(f"c0000001-0000-0000-0000-{n:012d}"),
            "term": term,
            "term_type": term_type,
            "definition": definition,
            "example_sentence": example,
            "is_catalog": True,
            "created_by_user_id": None,
        }

    rows = [
        _row(1,  "on",  "preposition",
             "Used for days, surfaces, and some time expressions (e.g. on Monday, on the table).",
             "The meeting is on Friday."),
        _row(2,  "in",  "preposition",
             "Used for enclosed spaces, months/years, and longer periods (e.g. in the room, in 2026).",
             "She lives in Berlin."),
        _row(3,  "at",  "preposition",
             "Used for specific times and places viewed as points (e.g. at 5 pm, at the station).",
             "We arrived at noon."),
        _row(4,  "by",  "preposition",
             "Often means near, before a deadline, or the agent in passive voice.",
             "Please finish by Tuesday."),
        _row(5,  "to",  "preposition",
             "Often indicates direction, purpose, or a recipient.",
             "I am going to the library."),
        _row(6,  "for", "preposition",
             "Used to indicate purpose, benefit, duration, or the recipient of an action.",
             "I bought this gift for you."),
        _row(7,  "with", "preposition",
             "Indicates accompaniment, means, or manner.",
             "She came with her friend."),
        _row(8,  "about", "preposition",
             "Concerning a topic or approximately.",
             "We talked about the project."),
        _row(9,  "from", "preposition",
             "Indicates origin, starting point, or source.",
             "He moved here from Madrid."),
        _row(10, "of",  "preposition",
             "Indicates belonging, quantity, or relationship.",
             "This is the end of the road."),
        _row(11, "into", "preposition",
             "Indicates movement toward the inside of something.",
             "She walked into the room."),
        _row(12, "through", "preposition",
             "Indicates movement from one side to the other, or a process.",
             "We drove through the tunnel."),
        _row(13, "over", "preposition",
             "Indicates position above, movement across, or more than.",
             "The plane flew over the city."),
        _row(14, "under", "preposition",
             "Indicates position below or fewer than.",
             "The cat is under the table."),
        _row(15, "between", "preposition",
             "Indicates a position or relationship involving two things.",
             "The shop is between the bank and the post office."),
        _row(16, "among", "preposition",
             "Indicates a position or relationship within a group of more than two.",
             "She was among the first to arrive."),
        _row(17, "after", "preposition",
             "Indicates following in time or order.",
             "We will meet after lunch."),
        _row(18, "before", "preposition",
             "Indicates earlier in time or in front of in place.",
             "Wash your hands before eating."),
        _row(19, "during", "preposition",
             "Indicates something that happens within a period of time.",
             "Please stay quiet during the film."),
        _row(20, "since", "preposition",
             "Indicates a starting point in time that continues to the present.",
             "I have lived here since 2018."),
        _row(21, "until", "preposition",
             "Indicates continuing up to a point in time.",
             "Wait here until I get back."),
        _row(22, "against", "preposition",
             "Indicates opposition or contact with a surface.",
             "The ladder leaned against the wall."),
        _row(23, "around", "preposition",
             "Indicates surrounding, approximately, or movement in a circle.",
             "We walked around the lake."),
        _row(24, "behind", "preposition",
             "Indicates a position at the back of something.",
             "The keys are behind the door."),
        _row(25, "beside", "preposition",
             "Indicates a position next to or at the side of something.",
             "She sat beside me on the train."),
        _row(26, "beyond", "preposition",
             "Indicates further than or outside the limits of.",
             "The village is beyond those hills."),
        _row(27, "despite", "preposition",
             "Indicates that something happens regardless of an obstacle.",
             "She finished the race despite the rain."),
        _row(28, "except", "preposition",
             "Indicates exclusion from a general statement.",
             "Everyone came except Tom."),
        _row(29, "along", "preposition",
             "Indicates movement following a line or path.",
             "We walked along the river."),
        _row(30, "across", "preposition",
             "Indicates movement from one side to the other, or a position on the other side.",
             "She swam across the lake."),
    ]
    op.bulk_insert(practice_terms_table, rows)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "DELETE FROM user_practice_term_selections "
        "WHERE practice_term_id IN ("
        "  SELECT id FROM practice_terms WHERE is_catalog = 1 AND created_by_user_id IS NULL"
        ")"
    ))
    conn.execute(sa.text(
        "DELETE FROM practice_terms WHERE is_catalog = 1 AND created_by_user_id IS NULL"
    ))
