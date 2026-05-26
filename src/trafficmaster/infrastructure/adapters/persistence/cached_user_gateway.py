import json
from typing import Final, override

from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.query_params.user_filters import UserParams
from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.cache.cache_store import CacheStore, CacheStoreError


class CachedUserGateway(UserGateway):
    ALL_USERS_TTL: Final[int] = 60
    USER_BY_ID_TTL: Final[int] = 300

    def __init__(self, user_gateway: UserGateway, cache_store: CacheStore) -> None:
        self._user_gateway: Final[UserGateway] = user_gateway
        self._cache_store: Final[CacheStore] = cache_store

    @staticmethod
    def _serialize_user(user: User) -> bytes:
        return json.dumps(user.serialize()).encode()

    @staticmethod
    def _deserialize_user(user: bytes) -> User:
        return User.deserialize(json.loads(user))

    def _serialize_users_list(self, users: list[User]) -> bytes:
        users_list: list[str] = [self._serialize_user(user).decode("utf-8") for user in users]
        return json.dumps(users_list).encode("utf-8")

    def _deserialize_users_list(self, data: bytes) -> list[User]:
        users_list: list[str] = json.loads(data)
        return [self._deserialize_user(user.encode("utf-8")) for user in users_list]

    @override
    async def read_by_id(self, user_id: UserID) -> User | None:
        cache_key: str = f"users:{user_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_user(cached_data)

            user: User | None = await self._user_gateway.read_by_id(user_id)

            if user:
                user_data = self._serialize_user(user)
                await self._cache_store.set(cache_key, user_data, self.USER_BY_ID_TTL)

        except CacheStoreError:
            return await self._user_gateway.read_by_id(user_id)
        else:
            return user

    @override
    async def read_by_email(self, user_email: UserEmail) -> User | None:
        cache_key: str = f"users:email:{user_email}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_user(cached_data)

            user: User | None = await self._user_gateway.read_by_email(user_email)

            if user:
                user_data = self._serialize_user(user)
                await self._cache_store.set(cache_key, user_data, self.USER_BY_ID_TTL)

        except CacheStoreError:
            return await self._user_gateway.read_by_email(user_email)
        else:
            return user

    @override
    async def read_all_users(self, user_params: UserParams) -> list[User]:
        cache_key: str = (
            f"users:all:"
            f"{user_params.pagination.limit}:{user_params.pagination.offset}:"
            f"{user_params.sorting_order.value}:{user_params.sorting_filter.value}"
        )
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_users_list(cached_data)

            users: list[User] = await self._user_gateway.read_all_users(user_params)

            if users:
                users_data = self._serialize_users_list(users)
                await self._cache_store.set(cache_key, users_data, self.ALL_USERS_TTL)

        except CacheStoreError:
            return await self._user_gateway.read_all_users(user_params)
        else:
            return users

    @override
    async def add(self, user: User) -> None:
        await self._user_gateway.add(user)
        try:
            await self._cache_store.delete(f"users:{user.id}")
            await self._cache_store.delete(f"users:email:{user.email}")
        except CacheStoreError:
            return

    @override
    async def delete_by_id(self, user_id: UserID) -> None:
        await self._user_gateway.delete_by_id(user_id)
        try:
            await self._cache_store.delete(f"users:{user_id}")
        except CacheStoreError:
            return
