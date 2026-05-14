from typing import Final, override

from sqlalchemy import delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.application.common.ports.auth.gateway import AuthSessionGateway
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.auth_sessions import auth_sessions_table


class AlchemyAuthSessionGateway(AuthSessionGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, auth_session: AuthSession) -> None:
        self._session.add(auth_session)

    @override
    async def update(self, auth_session: AuthSession) -> None:
        update_stmt = (
            update(AuthSession)
            .where(auth_sessions_table.c.id == auth_session.id_)
            .values(expiration=auth_session.expiration)
        )

        try:
            await self._session.execute(update_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, auth_session_id: str) -> AuthSession | None:
        try:
            auth_session: AuthSession | None = await self._session.get(AuthSession, auth_session_id)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return auth_session

    @override
    async def delete(self, auth_session_id: str) -> None:
        delete_stmt = delete(AuthSession).where(auth_sessions_table.c.id == auth_session_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_all_for_user(self, user_id: UserID) -> None:
        delete_stmt = delete(AuthSession).where(auth_sessions_table.c.user_id == user_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
