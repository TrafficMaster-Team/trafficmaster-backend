from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.views.deck.public_deck import PublicDeckView

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadPublicDecksQuery:
    limit: int | None = None
    offset: int | None = None


class ReadPublicDecksQueryHandler:
    def __init__(self, deck_gateway: DeckGateway) -> None:
        self._deck_gateway: Final[DeckGateway] = deck_gateway

    async def __call__(self, data: ReadPublicDecksQuery) -> list[PublicDeckView]:
        decks: list[Deck] = await self._deck_gateway.read_public_decks(
            pagination=Pagination(limit=data.limit, offset=data.offset),
        )

        return [
            PublicDeckView(
                id=deck.id,
                owner_id=deck.owner_id,
                title=str(deck.title),
                description=deck.description,
                created_at=deck.created_at,
                updated_at=deck.updated_at,
            )
            for deck in decks
        ]
