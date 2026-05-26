import json
from typing import Final, override

from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.cache.cache_store import CacheStore, CacheStoreError


class CachedDeckGateway(DeckGateway):
    DECK_BY_ID_TTL: Final[int] = 300
    USER_DECKS_TTL: Final[int] = 120
    PUBLIC_DECKS_TTL: Final[int] = 60
    COUNT_TTL: Final[int] = 60
    EXISTS_TTL: Final[int] = 60

    def __init__(self, deck_gateway: DeckGateway, cache_store: CacheStore) -> None:
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._cache_store: Final[CacheStore] = cache_store

    @staticmethod
    def _serialize_deck(deck: Deck) -> bytes:
        return json.dumps(deck.serialize()).encode("utf-8")

    @staticmethod
    def _deserialize_deck(data: bytes) -> Deck:
        return Deck.deserialize(json.loads(data))

    def _serialize_decks_list(self, decks: list[Deck]) -> bytes:
        decks_list: list[str] = [self._serialize_deck(deck).decode("utf-8") for deck in decks]
        return json.dumps(decks_list).encode("utf-8")

    def _deserialize_decks_list(self, data: bytes) -> list[Deck]:
        decks_list: list[str] = json.loads(data)
        return [self._deserialize_deck(deck.encode("utf-8")) for deck in decks_list]

    @override
    async def read_by_id(self, deck_id: DeckID) -> Deck | None:
        cache_key: str = f"decks:{deck_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_deck(cached_data)

            deck: Deck | None = await self._deck_gateway.read_by_id(deck_id)

            if deck:
                deck_data = self._serialize_deck(deck)
                await self._cache_store.set(cache_key, deck_data, self.DECK_BY_ID_TTL)

        except CacheStoreError:
            return await self._deck_gateway.read_by_id(deck_id)
        else:
            return deck

    @override
    async def read_by_user_id(self, user_id: UserID) -> list[Deck]:
        cache_key: str = f"decks:user:{user_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_decks_list(cached_data)

            decks: list[Deck] = await self._deck_gateway.read_by_user_id(user_id)

            if decks:
                decks_data = self._serialize_decks_list(decks)
                await self._cache_store.set(cache_key, decks_data, self.USER_DECKS_TTL)

        except CacheStoreError:
            return await self._deck_gateway.read_by_user_id(user_id)
        else:
            return decks

    @override
    async def read_public_decks(self, pagination: Pagination) -> list[Deck]:
        cache_key: str = f"decks:public:{pagination.limit}:{pagination.offset}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_decks_list(cached_data)

            decks: list[Deck] = await self._deck_gateway.read_public_decks(pagination)

            if decks:
                decks_data = self._serialize_decks_list(decks)
                await self._cache_store.set(cache_key, decks_data, self.PUBLIC_DECKS_TTL)

        except CacheStoreError:
            return await self._deck_gateway.read_public_decks(pagination)
        else:
            return decks

    @override
    async def count_by_user(self, user_id: UserID) -> int:
        cache_key: str = f"decks:count:user:{user_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return int(cached_data.decode("utf-8"))

            count: int = await self._deck_gateway.count_by_user(user_id)
            await self._cache_store.set(cache_key, str(count).encode("utf-8"), self.COUNT_TTL)

        except CacheStoreError:
            return await self._deck_gateway.count_by_user(user_id)
        else:
            return count

    @override
    async def exists_with_deck_config_id(self, deck_config_id: DeckConfigID) -> bool:
        cache_key: str = f"decks:exists_config:{deck_config_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return cached_data == b"1"

            exists: bool = await self._deck_gateway.exists_with_deck_config_id(deck_config_id)
            await self._cache_store.set(cache_key, b"1" if exists else b"0", self.EXISTS_TTL)

        except CacheStoreError:
            return await self._deck_gateway.exists_with_deck_config_id(deck_config_id)
        else:
            return exists

    @override
    async def add(self, deck: Deck) -> None:
        await self._deck_gateway.add(deck)
        try:
            await self._cache_store.delete(f"decks:{deck.id}")
            await self._cache_store.delete(f"decks:user:{deck.owner_id}")
            await self._cache_store.delete(f"decks:count:user:{deck.owner_id}")
            await self._cache_store.delete(f"decks:exists_config:{deck.deck_config_id}")
        except CacheStoreError:
            return

    @override
    async def delete_by_id(self, deck_id: DeckID) -> None:
        cached_owner_id: UserID | None = None
        cached_config_id: DeckConfigID | None = None
        try:
            cached_data: bytes | None = await self._cache_store.get(f"decks:{deck_id}")
            if cached_data:
                deck = self._deserialize_deck(cached_data)
                cached_owner_id = deck.owner_id
                cached_config_id = deck.deck_config_id
        except CacheStoreError:
            pass  # best-effort peek; proceed without owner/config invalidation

        await self._deck_gateway.delete_by_id(deck_id)

        try:
            await self._cache_store.delete(f"decks:{deck_id}")
            if cached_owner_id is not None:
                await self._cache_store.delete(f"decks:user:{cached_owner_id}")
                await self._cache_store.delete(f"decks:count:user:{cached_owner_id}")
            if cached_config_id is not None:
                await self._cache_store.delete(f"decks:exists_config:{cached_config_id}")
        except CacheStoreError:
            return
