from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.user.values.user_id import UserID


class CardProgressGateway(Protocol):
    @abstractmethod
    async def add(self, progress: CardProgress) -> None: ...

    @abstractmethod
    async def delete_by_id(self, progress_id: CardProgressID) -> None: ...

    @abstractmethod
    async def read_by_id(self, card_progress_id: CardProgressID) -> CardProgress | None: ...

    @abstractmethod
    async def read_by_user_and_card(
        self,
        user_id: UserID,
        card_id: CardID,
    ) -> CardProgress | None: ...
