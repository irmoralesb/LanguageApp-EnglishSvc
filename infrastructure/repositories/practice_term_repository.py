import uuid
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.practice_term_model import PracticeTermModel
from domain.interfaces.practice_term_repository import PracticeTermRepositoryInterface
from infrastructure.databases.models import PracticeTermDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class PracticeTermRepository(PracticeTermRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='read', entity_type='practice_term')
    @trace_database_operation(operation_type='select', table='practice_terms')
    @track_database_operation(operation_type='select', table='practice_terms')
    async def get_by_id(self, practice_term_id: UUID) -> PracticeTermModel | None:
        result = await self.db.execute(
            select(PracticeTermDataModel).where(PracticeTermDataModel.id == practice_term_id)
        )
        row = result.scalars().first()
        return self._to_domain(row) if row else None

    @log_database_operation_decorator(operation_type='query', entity_type='practice_term')
    @trace_database_operation(operation_type='select', table='practice_terms')
    @track_database_operation(operation_type='select', table='practice_terms')
    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PracticeTermModel]:
        result = await self.db.execute(
            select(PracticeTermDataModel)
            .where(PracticeTermDataModel.is_catalog == True)
            .order_by(PracticeTermDataModel.term_type, PracticeTermDataModel.term)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='practice_term')
    @trace_database_operation(operation_type='select', table='practice_terms')
    @track_database_operation(operation_type='select', table='practice_terms')
    async def get_by_user(self, user_id: UUID) -> list[PracticeTermModel]:
        result = await self.db.execute(
            select(PracticeTermDataModel)
            .where(
                PracticeTermDataModel.is_catalog == False,
                PracticeTermDataModel.created_by_user_id == user_id,
            )
            .order_by(PracticeTermDataModel.term)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='create', entity_type='practice_term')
    @trace_database_operation(operation_type='insert', table='practice_terms')
    @track_database_operation(operation_type='insert', table='practice_terms')
    async def create(self, practice_term: PracticeTermModel) -> PracticeTermModel:
        db_item = PracticeTermDataModel(
            id=practice_term.id or uuid.uuid4(),
            term=practice_term.term,
            term_type=practice_term.term_type,
            definition=practice_term.definition,
            example_sentence=practice_term.example_sentence,
            is_catalog=practice_term.is_catalog,
            created_by_user_id=practice_term.created_by_user_id,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='update', entity_type='practice_term')
    @trace_database_operation(operation_type='update', table='practice_terms')
    @track_database_operation(operation_type='update', table='practice_terms')
    async def update(self, practice_term: PracticeTermModel) -> PracticeTermModel | None:
        result = await self.db.execute(
            select(PracticeTermDataModel).where(PracticeTermDataModel.id == practice_term.id)
        )
        db_item = result.scalars().first()
        if db_item is None:
            return None

        db_item.term = practice_term.term
        db_item.term_type = practice_term.term_type
        db_item.definition = practice_term.definition
        db_item.example_sentence = practice_term.example_sentence

        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='delete', entity_type='practice_term')
    @trace_database_operation(operation_type='delete', table='practice_terms')
    @track_database_operation(operation_type='delete', table='practice_terms')
    async def delete(self, practice_term_id: UUID) -> bool:
        result = await self.db.execute(
            delete(PracticeTermDataModel).where(PracticeTermDataModel.id == practice_term_id)
        )
        return result.rowcount > 0

    @staticmethod
    def _to_domain(row: PracticeTermDataModel) -> PracticeTermModel:
        return PracticeTermModel(
            id=row.id,
            term=row.term,
            term_type=row.term_type,
            definition=row.definition,
            example_sentence=row.example_sentence,
            is_catalog=row.is_catalog,
            created_by_user_id=row.created_by_user_id,
            created_at=row.created_at,
        )
