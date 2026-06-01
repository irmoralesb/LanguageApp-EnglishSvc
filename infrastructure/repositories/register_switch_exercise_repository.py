import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.register_switch_exercise_model import RegisterSwitchHistoryRecord
from domain.interfaces.register_switch_exercise_repository import (
    RegisterSwitchExerciseRepositoryInterface,
)
from infrastructure.databases.models import RegisterSwitchExerciseResultDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.metrics.decorators import track_database_operation
from infrastructure.observability.tracing.decorators import trace_database_operation


_TABLE = "register_switch_exercise_results"


class RegisterSwitchExerciseRepository(RegisterSwitchExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='register_switch_exercise_result')
    @trace_database_operation(operation_type='insert', table=_TABLE)
    @track_database_operation(operation_type='insert', table=_TABLE)
    async def save_result(
        self, record: RegisterSwitchHistoryRecord,
    ) -> RegisterSwitchHistoryRecord:
        db_item = RegisterSwitchExerciseResultDataModel(
            id=record.id or uuid.uuid4(),
            user_id=record.user_id,
            target_language_code=record.target_language_code,
            scenario_native=record.scenario_native,
            source_sentence=record.source_sentence,
            source_register=record.source_register,
            target_register=record.target_register,
            slang_level=record.slang_level,
            user_answer=record.user_answer,
            is_correct=record.is_correct,
            feedback=record.feedback,
            model_answer=record.model_answer,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='register_switch_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[RegisterSwitchHistoryRecord]:
        result = await self.db.execute(
            select(RegisterSwitchExerciseResultDataModel)
            .where(RegisterSwitchExerciseResultDataModel.user_id == user_id)
            .order_by(RegisterSwitchExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @staticmethod
    def _to_domain(row: RegisterSwitchExerciseResultDataModel) -> RegisterSwitchHistoryRecord:
        return RegisterSwitchHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            target_language_code=row.target_language_code,
            scenario_native=row.scenario_native,
            source_sentence=row.source_sentence,
            source_register=row.source_register,
            target_register=row.target_register,
            slang_level=row.slang_level,
            user_answer=row.user_answer,
            is_correct=row.is_correct,
            feedback=row.feedback,
            model_answer=row.model_answer,
            created_at=row.created_at,
        )
