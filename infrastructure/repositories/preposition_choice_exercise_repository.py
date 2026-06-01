import uuid
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.preposition_choice_exercise_model import (
    PrepositionChoiceHistoryRecord,
    PrepositionChoicePairStats,
)
from domain.interfaces.preposition_choice_exercise_repository import (
    PrepositionChoiceExerciseRepositoryInterface,
)
from domain.preposition_choice_pairs import normalize_pair
from infrastructure.databases.models import PrepositionChoiceExerciseResultDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


_TABLE = "preposition_choice_exercise_results"


class PrepositionChoiceExerciseRepository(PrepositionChoiceExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='preposition_choice_exercise_result')
    @trace_database_operation(operation_type='insert', table=_TABLE)
    @track_database_operation(operation_type='insert', table=_TABLE)
    async def save_result(
        self, record: PrepositionChoiceHistoryRecord,
    ) -> PrepositionChoiceHistoryRecord:
        db_item = PrepositionChoiceExerciseResultDataModel(
            id=record.id or uuid.uuid4(),
            user_id=record.user_id,
            option_a=record.option_a,
            option_b=record.option_b,
            target_language_code=record.target_language_code,
            scenario_native=record.scenario_native,
            sentence_with_blank=record.sentence_with_blank,
            sentence_complete=record.sentence_complete,
            correct_preposition=record.correct_preposition,
            user_answer=record.user_answer,
            is_correct=record.is_correct,
            feedback=record.feedback,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='preposition_choice_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[PrepositionChoiceHistoryRecord]:
        result = await self.db.execute(
            select(PrepositionChoiceExerciseResultDataModel)
            .where(PrepositionChoiceExerciseResultDataModel.user_id == user_id)
            .order_by(PrepositionChoiceExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='preposition_choice_exercise_result')
    @trace_database_operation(operation_type='select', table=_TABLE)
    @track_database_operation(operation_type='select', table=_TABLE)
    async def get_pair_stats_by_user(self, user_id: UUID) -> list[PrepositionChoicePairStats]:
        stmt = (
            select(
                PrepositionChoiceExerciseResultDataModel.option_a,
                PrepositionChoiceExerciseResultDataModel.option_b,
                func.sum(
                    case((PrepositionChoiceExerciseResultDataModel.is_correct == True, 1), else_=0)  # noqa: E712
                ).label("correct_count"),
                func.sum(
                    case((PrepositionChoiceExerciseResultDataModel.is_correct == False, 1), else_=0)  # noqa: E712
                ).label("incorrect_count"),
            )
            .where(PrepositionChoiceExerciseResultDataModel.user_id == user_id)
            .group_by(
                PrepositionChoiceExerciseResultDataModel.option_a,
                PrepositionChoiceExerciseResultDataModel.option_b,
            )
        )
        result = await self.db.execute(stmt)
        merged: dict[tuple[str, str], PrepositionChoicePairStats] = {}
        for row in result.all():
            a, b = normalize_pair(row.option_a, row.option_b)
            key = (a, b)
            existing = merged.get(key)
            if existing is None:
                merged[key] = PrepositionChoicePairStats(
                    option_a=a,
                    option_b=b,
                    correct_count=row.correct_count or 0,
                    incorrect_count=row.incorrect_count or 0,
                )
            else:
                existing.correct_count += row.correct_count or 0
                existing.incorrect_count += row.incorrect_count or 0
        return list(merged.values())

    @staticmethod
    def _to_domain(row: PrepositionChoiceExerciseResultDataModel) -> PrepositionChoiceHistoryRecord:
        a, b = normalize_pair(row.option_a, row.option_b)
        return PrepositionChoiceHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            option_a=a,
            option_b=b,
            target_language_code=row.target_language_code,
            scenario_native=row.scenario_native,
            sentence_with_blank=row.sentence_with_blank,
            sentence_complete=row.sentence_complete,
            correct_preposition=row.correct_preposition.strip().lower(),
            user_answer=row.user_answer,
            is_correct=row.is_correct,
            feedback=row.feedback,
            created_at=row.created_at,
        )
