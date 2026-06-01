import uuid
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.english_expression_model import EnglishExpressionModel
from domain.interfaces.english_expression_repository import EnglishExpressionRepositoryInterface
from infrastructure.databases.models import EnglishExpressionDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.metrics.decorators import track_database_operation
from infrastructure.observability.tracing.decorators import trace_database_operation


class EnglishExpressionRepository(EnglishExpressionRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='read', entity_type='english_expression')
    @trace_database_operation(operation_type='select', table='english_expressions')
    @track_database_operation(operation_type='select', table='english_expressions')
    async def get_by_id(self, english_expression_id: UUID) -> EnglishExpressionModel | None:
        result = await self.db.execute(
            select(EnglishExpressionDataModel).where(
                EnglishExpressionDataModel.id == english_expression_id
            )
        )
        row = result.scalars().first()
        return self._to_domain(row) if row else None

    @log_database_operation_decorator(operation_type='query', entity_type='english_expression')
    @trace_database_operation(operation_type='select', table='english_expressions')
    @track_database_operation(operation_type='select', table='english_expressions')
    async def get_catalog(
        self, skip: int = 0, limit: int = 100, expression_type: str | None = None,
    ) -> list[EnglishExpressionModel]:
        stmt = (
            select(EnglishExpressionDataModel)
            .where(EnglishExpressionDataModel.is_catalog == True)  # noqa: E712
            .order_by(EnglishExpressionDataModel.text)
            .offset(skip)
            .limit(limit)
        )
        if expression_type is not None:
            stmt = stmt.where(EnglishExpressionDataModel.expression_type == expression_type)
        result = await self.db.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='english_expression')
    @trace_database_operation(operation_type='select', table='english_expressions')
    @track_database_operation(operation_type='select', table='english_expressions')
    async def get_by_user(self, user_id: UUID) -> list[EnglishExpressionModel]:
        result = await self.db.execute(
            select(EnglishExpressionDataModel)
            .where(
                EnglishExpressionDataModel.is_catalog == False,  # noqa: E712
                EnglishExpressionDataModel.created_by_user_id == user_id,
            )
            .order_by(EnglishExpressionDataModel.text)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='create', entity_type='english_expression')
    @trace_database_operation(operation_type='insert', table='english_expressions')
    @track_database_operation(operation_type='insert', table='english_expressions')
    async def create(self, expression: EnglishExpressionModel) -> EnglishExpressionModel:
        db_item = EnglishExpressionDataModel(
            id=expression.id or uuid.uuid4(),
            text=expression.text,
            expression_type=expression.expression_type,
            definition=expression.definition,
            example_sentence=expression.example_sentence,
            register=expression.register,
            is_catalog=expression.is_catalog,
            created_by_user_id=expression.created_by_user_id,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='update', entity_type='english_expression')
    @trace_database_operation(operation_type='update', table='english_expressions')
    @track_database_operation(operation_type='update', table='english_expressions')
    async def update(self, expression: EnglishExpressionModel) -> EnglishExpressionModel | None:
        result = await self.db.execute(
            select(EnglishExpressionDataModel).where(
                EnglishExpressionDataModel.id == expression.id
            )
        )
        db_item = result.scalars().first()
        if db_item is None:
            return None
        db_item.text = expression.text
        db_item.expression_type = expression.expression_type
        db_item.definition = expression.definition
        db_item.example_sentence = expression.example_sentence
        db_item.register = expression.register
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='delete', entity_type='english_expression')
    @trace_database_operation(operation_type='delete', table='english_expressions')
    @track_database_operation(operation_type='delete', table='english_expressions')
    async def delete(self, english_expression_id: UUID) -> bool:
        result = await self.db.execute(
            delete(EnglishExpressionDataModel).where(
                EnglishExpressionDataModel.id == english_expression_id
            )
        )
        return result.rowcount > 0

    @staticmethod
    def _to_domain(row: EnglishExpressionDataModel) -> EnglishExpressionModel:
        return EnglishExpressionModel(
            id=row.id,
            text=row.text,
            expression_type=row.expression_type,
            definition=row.definition,
            example_sentence=row.example_sentence,
            register=row.register,
            is_catalog=row.is_catalog,
            created_by_user_id=row.created_by_user_id,
            created_at=row.created_at,
        )
