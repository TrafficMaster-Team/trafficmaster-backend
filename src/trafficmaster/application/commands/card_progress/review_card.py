from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.card_progress.review_card import ReviewCardView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.deck import DeckConfigNotFoundError, DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.services.card_progress_service import CardProgressService
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
    from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewCardCommand:
    card_id: UUID
    rating: ReviewRating


class ReviewCardCommandHandler:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        card_gateway: CardGateway,
        current_user_service: CurrentUserService,
        deck_gateway: DeckGateway,
        deck_config_gateway: DeckConfigGateway,
        user_gateway: UserGateway,
        access_service: AccessService,
        card_progress_service: CardProgressService,
        card_progress_gateway: CardProgressGateway,
        review_log_gateway: ReviewLogGateway,
    ) -> None:
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._card_gateway: Final[CardGateway] = card_gateway
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._card_progress_service: Final[CardProgressService] = card_progress_service
        self._card_progress_gateway: Final[CardProgressGateway] = card_progress_gateway
        self._review_log_gateway: Final[ReviewLogGateway] = review_log_gateway

    async def __call__(self, data: ReviewCardCommand) -> ReviewCardView:

        current_user: User = await self._current_user_service.get_current_user()

        card: Card | None = await self._card_gateway.read_by_id(CardID(data.card_id))

        if card is None:
            msg = "Card not found"
            raise CardNotFoundError(msg)

        deck: Deck | None = await self._deck_gateway.read_deck_by_id(DeckID(card.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        deck_owner: User | None = await self._user_gateway.read_by_id(UserID(deck.owner_id))

        if deck_owner is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not deck.is_public and not self._access_service.can_manage_user(
            subject=current_user,
            target=deck_owner,
        ):
            msg = "You don't have access to this card"
            raise NoPermissionToManageUserError(msg)

        deck_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(
            DeckConfigID(deck.deck_config_id),
        )

        if deck_config is None:
            msg = "Deck config not found"
            raise DeckConfigNotFoundError(msg)

        progress: CardProgress | None = await self._card_progress_gateway.read_by_user_and_card(
            user_id=current_user.id,
            card_id=card.id,
        )

        if progress is None:
            progress = self._card_progress_service.create_card_progress(
                user_id=current_user.id,
                card_id=card.id,
                default_ease_factor=EaseFactor(deck_config.advanced.ease_factor),
            )
            await self._card_progress_gateway.add(progress)

        review_log: ReviewLog = self._card_progress_service.schedule(
            progress=progress,
            rating=data.rating,
            deck=deck_config,
        )

        await self._review_log_gateway.add(review_log)

        await self._transaction_manager.commit()

        return ReviewCardView(
            card_progress_id=progress.id,
            review_log_id=review_log.id,
            state=progress.state,
            interval=progress.interval.value,
            next_review_at=progress.next_review_at,
        )
