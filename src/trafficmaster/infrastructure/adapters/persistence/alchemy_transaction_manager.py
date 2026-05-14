from typing import Final, override

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.infrastructure.adapters.persistence.constants import (
    DB_CONSTRAINT_VIOLATION,
    DB_QUERY_FAILED,
    DB_ROLLBACK_FAILED,
)
from trafficmaster.infrastructure.errors.transaction_manager import EntityAddError, RollbackError


class SqlAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def commit(self) -> None:

        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise EntityAddError(DB_CONSTRAINT_VIOLATION) from error
        except SQLAlchemyError as error:
            await self._session.rollback()
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def rollback(self) -> None:

        try:
            await self._session.rollback()
        except SQLAlchemyError as error:
            raise RollbackError(DB_ROLLBACK_FAILED) from error

    @override
    async def flush(self) -> None:

        try:
            await self._session.flush()
        except IntegrityError as error:
            raise EntityAddError(DB_CONSTRAINT_VIOLATION) from error
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
