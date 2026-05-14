from typing import TYPE_CHECKING, Final, override

from sqlalchemy import ColumnElement, Delete, Result, Select, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.query_params.user_filters import UserParams
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.application.errors.query_params import SortingError
from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.users import users_table

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from trafficmaster.domain.user.values.user_role import UserRole


class AlchemyUserGateway(UserGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, user: User) -> None:
        self._session.add(user)

    @override
    async def delete_by_id(self, user_id: UserID) -> None:
        delete_stmt: Delete = delete(User).where(users_table.c.id == user_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, user_id: UserID) -> User | None:
        select_stmt: Select[tuple[User]] = select(User).where(users_table.c.id == user_id)

        try:
            rows: Result[tuple[User]] = await self._session.execute(select_stmt)
            user: User | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return user

    @override
    async def read_by_email(self, user_email: UserEmail) -> User | None:
        select_stmt: Select[tuple[User]] = select(User).where(users_table.c.email == str(user_email))

        try:
            rows: Result[tuple[User]] = await self._session.execute(select_stmt)
            user: User | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return user

    @override
    async def read_all_users(self, user_params: UserParams) -> list[User]:
        sorting_field: ColumnElement[UUID | str | UserRole] | None = users_table.c.get(user_params.sorting_filter)

        if sorting_field is None:
            msg = f"Unknown sorting field: {user_params.sorting_filter}"
            raise SortingError(msg)

        order_by_param: ColumnElement[UUID | str | UserRole] = (
            sorting_field.asc() if user_params.sorting_order == SortingOrder.ASC else sorting_field.desc()
        )

        select_stmt: Select[tuple[User]] = (
            select(User)
            .order_by(order_by_param)
            .limit(user_params.pagination.limit)
            .offset(user_params.pagination.offset)
        )

        try:
            rows: Result[tuple[User]] = await self._session.execute(select_stmt)
            users: Sequence[User] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return list(users)
