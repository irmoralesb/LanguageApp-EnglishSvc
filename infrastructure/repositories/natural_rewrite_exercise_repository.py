import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.natural_rewrite_exercise_model import NaturalRewriteHistoryRecord
from domain.interfaces.natural_rewrite_exercise_repository import (
    NaturalRewriteExerciseRepositoryInterface,
)
from infrastructure.databases.models import NaturalRewriteExerciseResultDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.metrics.decorators import track_database_operation
from infrastructure.observability.tracing.decorators import trace_database_operation


_TABLE = "natural_rewrite_exercise_results"


class NaturalRewriteExerciseRepository(NaturalRewriteExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='natural_rewrite_exercise_result')
    @trace_database_operation(operation_type='insert', table=_TABLE)
    @track_database_operation(operation_type='insert', table=_TABLE)
    async def save_result(
        self, record: NaturalRewriteHistoryRecord,
    ) -> NaturalRewriteHistoryRecord:
        db_item = NaturalRewriteExerciseResultDataModel(
            id=record.id or uuid.uuid4(),
            user_id=record.user_id,
            target_language_code=record.target_language_code,
            scenario_native=record.scenario_native,
            stiff_sentence=record.stiff_sentence,
            user_answer=record.user_answer,
            is_correct=record.is_correct,
            feedback=record.feedback,
            model_answer=record.model_answer,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='natural_rewrite_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[NaturalRewriteHistoryRecord]:
        result = await self.db.execute(
            select(NaturalRewriteExerciseResultDataModel)
            .where(NaturalRewriteExerciseResultDataModel.user_id == user_id)
            .order_by(NaturalRewriteExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @staticmethod
    def _to_domain(row: NaturalRewriteExerciseResultDataModel) -> NaturalRewriteHistoryRecord:
        return NaturalRewriteHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            target_language_code=row.target_language_code,
            scenario_native=row.scenario_native,
            stiff_sentence=row.stiff_sentence,
            user_answer=row.user_answer,
            is_correct=row.is_correct,
            feedback=row.feedback,
            model_answer=row.model_answer,
            created_at=row.created_at,
        )
