from datetime import datetime
from typing import Protocol

from trafficmaster.application.common.ports.card_progress.card_with_progress import CardWithProgress
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder
from trafficmaster.domain.user.values.user_id import UserID


class CardProgressGateway(Protocol):
    async def add(self, progress: CardProgress) -> None: ...

    async def delete_by_id(self, progress_id: CardProgressID) -> None: ...

    async def read_by_id(self, progress_id: CardProgressID) -> CardProgress | None: ...

    async def read_by_user_and_card(
        self,
        user_id: UserID,
        card_id: CardID,
    ) -> CardProgress | None: ...

    async def read_due_learning(
        self, user_id: UserID, deck_id: DeckID, now: datetime, limit: int
    ) -> list[CardWithProgress]: ...

    async def read_due_review(
        self, user_id: UserID, deck_id: DeckID, now: datetime, limit: int
    ) -> list[CardWithProgress]: ...

    async def read_new_cards(
        self,
        user_id: UserID,
        deck_id: DeckID,
        now: datetime,
        limit: int,
        order: NewCardOrder,
    ) -> list[CardWithProgress]: ...

    async def count_by_state(self, user_id: UserID, deck_id: DeckID | None) -> dict[CardState | None, int]: ...

    async def count_due_learning(self, user_id: UserID, deck_id: DeckID | None, now: datetime) -> int: ...

    async def count_due_review(self, user_id: UserID, deck_id: DeckID | None, now: datetime) -> int: ...
