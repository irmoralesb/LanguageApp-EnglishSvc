import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.multiple_prepositions_exercise_model import (
    MultiplePrepositionsExerciseHistoryRecord,
)
from domain.interfaces.multiple_prepositions_exercise_repository import (
    MultiplePrepositionsExerciseRepositoryInterface,
)
from infrastructure.databases.models import (
    MultiplePrepositionsExerciseResultDataModel,
    MultiplePrepositionsExerciseResultTermDataModel,
)
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


_TABLE = "multiple_prepositions_exercise_results"


class MultiplePrepositionsExerciseRepository(MultiplePrepositionsExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='multiple_prepositions_exercise_result')
    @trace_database_operation(operation_type='insert', table=_TABLE)
    @track_database_operation(operation_type='insert', table=_TABLE)
    async def save_attempt(
        self, record: MultiplePrepositionsExerciseHistoryRecord,
    ) -> MultiplePrepositionsExerciseHistoryRecord:
        result_id = record.id or uuid.uuid4()
        db_item = MultiplePrepositionsExerciseResultDataModel(
            id=result_id,
            user_id=record.user_id,
            target_language_code=record.target_language_code,
            sentence_native=record.sentence_native,
            sentence_target=record.sentence_target,
            user_answer=record.user_answer,
            attempt_number=record.attempt_number,
            is_correct=record.is_correct,
            feedback=record.feedback,
            revealed=record.revealed,
        )
        for index, term_id in enumerate(record.practice_term_ids):
            db_item.terms.append(
                MultiplePrepositionsExerciseResultTermDataModel(
                    result_id=result_id,
                    practice_term_id=term_id,
                    position=index,
                )
            )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='multiple_prepositions_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[MultiplePrepositionsExerciseHistoryRecord]:
        result = await self.db.execute(
            select(MultiplePrepositionsExerciseResultDataModel)
            .where(MultiplePrepositionsExerciseResultDataModel.user_id == user_id)
            .order_by(MultiplePrepositionsExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().unique().all()]

    @staticmethod
    def _to_domain(
        row: MultiplePrepositionsExerciseResultDataModel,
    ) -> MultiplePrepositionsExerciseHistoryRecord:
        ordered_terms = sorted(row.terms, key=lambda t: t.position)
        return MultiplePrepositionsExerciseHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            practice_term_ids=[t.practice_term_id for t in ordered_terms],
            target_language_code=row.target_language_code,
            sentence_native=row.sentence_native,
            sentence_target=row.sentence_target,
            user_answer=row.user_answer,
            attempt_number=row.attempt_number,
            is_correct=row.is_correct,
            feedback=row.feedback,
            revealed=row.revealed,
            created_at=row.created_at,
        )
