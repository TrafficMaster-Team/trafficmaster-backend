from dataclasses import dataclass

from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress


@dataclass(frozen=True, slots=True, kw_only=True)
class CardWithProgress:
    card: Card
    progress: CardProgress | None
