import json
from typing import Final, override

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.cache.cache_store import CacheStore


class CachedDeckConfigQueryGateway(DeckConfigGateway):
    DECK_CONFIG_BY_ID_TTL: Final[int] = 600
    USER_DECK_CONFIGS_TTL: Final[int] = 300

    def __init__(self, deck_config_gateway: DeckConfigGateway, cache_store: CacheStore) -> None:
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._cache_store: Final[CacheStore] = cache_store

    @staticmethod
    def _serialize_deck_config(deck_config: DeckConfig) -> bytes:
        return json.dumps(deck_config.serialize()).encode("utf-8")

    @staticmethod
    def _deserialize_deck_config(data: bytes) -> DeckConfig:
        return DeckConfig.deserialize(json.loads(data))

    def _serialize_deck_configs_list(self, deck_configs: list[DeckConfig]) -> bytes:
        configs_list: list[str] = [self._serialize_deck_config(cfg).decode("utf-8") for cfg in deck_configs]
        return json.dumps(configs_list).encode("utf-8")

    def _deserialize_deck_configs_list(self, data: bytes) -> list[DeckConfig]:
        configs_list: list[str] = json.loads(data)
        return [self._deserialize_deck_config(cfg.encode("utf-8")) for cfg in configs_list]

    @override
    async def read_by_id(self, deck_config_id: DeckConfigID) -> DeckConfig | None:
        cache_key: str = f"deck_configs:{deck_config_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_deck_config(cached_data)

            deck_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(deck_config_id)

            if deck_config:
                config_data = self._serialize_deck_config(deck_config)
                await self._cache_store.set(cache_key, config_data, self.DECK_CONFIG_BY_ID_TTL)

        except Exception:  # noqa: BLE001  # cache failures must fall back to the underlying gateway
            return await self._deck_config_gateway.read_by_id(deck_config_id)
        else:
            return deck_config

    @override
    async def read_by_user_id(self, user_id: UserID) -> list[DeckConfig]:
        cache_key: str = f"deck_configs:user:{user_id}"
        try:
            cached_data: bytes | None = await self._cache_store.get(cache_key)
            if cached_data:
                return self._deserialize_deck_configs_list(cached_data)

            deck_configs: list[DeckConfig] = await self._deck_config_gateway.read_by_user_id(user_id)

            if deck_configs:
                configs_data = self._serialize_deck_configs_list(deck_configs)
                await self._cache_store.set(cache_key, configs_data, self.USER_DECK_CONFIGS_TTL)

        except Exception:  # noqa: BLE001  # cache failures must fall back to the underlying gateway
            return await self._deck_config_gateway.read_by_user_id(user_id)
        else:
            return deck_configs

    @override
    async def add(self, deck_config: DeckConfig) -> None:
        await self._deck_config_gateway.add(deck_config)
        try:
            await self._cache_store.delete(f"deck_configs:{deck_config.id}")
            await self._cache_store.delete(f"deck_configs:user:{deck_config.owner_id}")
        except Exception:  # noqa: BLE001  # cache failures must fall back to the underlying gateway
            return

    @override
    async def delete_by_id(self, deck_config_id: DeckConfigID) -> None:
        cached_owner_id: UserID | None = None
        try:
            cached_data: bytes | None = await self._cache_store.get(f"deck_configs:{deck_config_id}")
            if cached_data:
                cached_owner_id = self._deserialize_deck_config(cached_data).owner_id
        except Exception:  # noqa: BLE001, S110  # best-effort peek; proceed without owner invalidation
            pass

        await self._deck_config_gateway.delete_by_id(deck_config_id)

        try:
            await self._cache_store.delete(f"deck_configs:{deck_config_id}")
            if cached_owner_id is not None:
                await self._cache_store.delete(f"deck_configs:user:{cached_owner_id}")
        except Exception:  # noqa: BLE001  # cache failures must fall back to the underlying gateway
            return
