import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.expression_exercise_model import ExpressionExerciseHistoryRecord
from domain.interfaces.expression_exercise_repository import (
    ExpressionExerciseRepositoryInterface,
)
from infrastructure.databases.models import EnglishExpressionExerciseResultDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.metrics.decorators import track_database_operation
from infrastructure.observability.tracing.decorators import trace_database_operation


_TABLE = "english_expression_exercise_results"


class ExpressionExerciseRepository(ExpressionExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='expression_exercise_result')
    @trace_database_operation(operation_type='insert', table=_TABLE)
    @track_database_operation(operation_type='insert', table=_TABLE)
    async def save_result(
        self, record: ExpressionExerciseHistoryRecord,
    ) -> ExpressionExerciseHistoryRecord:
        db_item = EnglishExpressionExerciseResultDataModel(
            id=record.id or uuid.uuid4(),
            user_id=record.user_id,
            english_expression_id=record.english_expression_id,
            exercise_type=record.exercise_type,
            target_language_code=record.target_language_code,
            scenario_native=record.scenario_native,
            prompt_native=record.prompt_native,
            expected_answer=record.expected_answer,
            user_answer=record.user_answer,
            is_correct=record.is_correct,
            feedback=record.feedback,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='expression_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExpressionExerciseHistoryRecord]:
        result = await self.db.execute(
            select(EnglishExpressionExerciseResultDataModel)
            .where(EnglishExpressionExerciseResultDataModel.user_id == user_id)
            .order_by(EnglishExpressionExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @staticmethod
    def _to_domain(
        row: EnglishExpressionExerciseResultDataModel,
    ) -> ExpressionExerciseHistoryRecord:
        return ExpressionExerciseHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            english_expression_id=row.english_expression_id,
            exercise_type=row.exercise_type,
            target_language_code=row.target_language_code,
            scenario_native=row.scenario_native,
            prompt_native=row.prompt_native,
            expected_answer=row.expected_answer,
            user_answer=row.user_answer,
            is_correct=row.is_correct,
            feedback=row.feedback,
            created_at=row.created_at,
        )
