from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

import pydantic
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from trafficmaster.application.errors.auth import (
    AlreadyAuthenticatedError,
    AuthenticationError,
    AuthorizationError,
)
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.card_progress import CardProgressNotFoundError
from trafficmaster.application.errors.deck import (
    DeckConfigInUseError,
    DeckConfigNotFoundError,
    DeckNotFoundError,
)
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.application.errors.query_params import PaginationError, SortingError
from trafficmaster.application.errors.user import (
    EmailAlreadyExistsError,
    NoPermissionToManageUserError,
    UserAlreadyExistsError,
    UserNotFoundByEmailError,
    UserNotFoundByIdError,
)
from trafficmaster.domain.card.errors.card import (
    CardAnswerEmptyError,
    CardQuestionEmptyError,
    CardTagNotFoundError,
    DuplicateCardTagError,
    EmptyCardTagError,
    TooLongAnswerError,
    TooLongCardTagError,
    TooLongQuestionError,
    TooShortAnswerError,
    TooShortCardTagError,
    TooShortQuestionError,
)
from trafficmaster.domain.card_progress.errors.card_progress import (
    TooLowEaseFactorError,
    TooLowIntervalError,
)
from trafficmaster.domain.common.errors import DomainFieldError, InconsistentTimeError
from trafficmaster.domain.deck.errors.deck import DeckTitleEmptyError
from trafficmaster.domain.deck.errors.deck_config import (
    DeckConfigNameEmptyError,
    HardIntervalNotLessThanEaseFactorError,
    InvalidIntervalModifierError,
    InvalidNewIntervalError,
    LearningIntervalGreaterGraduatingError,
    NewGreaterThanReviewedError,
    NotEnoughLearningStepsError,
    TooBigCardLimitError,
    TooLowEasyFactorError,
    TooLowMaxIntervalError,
    TooLowStepIntervalError,
    TooSmallCardLimitError,
    TooSmallLeechThresholdError,
    TooSmallMinRepeatIntervalError,
)
from trafficmaster.domain.user.errors.password import (
    PasswordCantBeEmptyError,
    WeakPasswordWasProvidedError,
)
from trafficmaster.domain.user.errors.user import (
    AccessChangeNotPermittedError,
    BadUsernameError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
    TooBigUsernameError,
    TooSmallUsernameError,
    UsernameCantBeEmptyError,
    WrongUserEmailFormatError,
)
from trafficmaster.infrastructure.errors.base import InfrastructureError
from trafficmaster.infrastructure.errors.transaction_manager import (
    EntityAddError,
    RollbackError,
)


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionHandler:
    _ERROR_MAPPING: Final[MappingProxyType[type[Exception], int]] = MappingProxyType(
        {
            # 400
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            InconsistentTimeError: status.HTTP_400_BAD_REQUEST,
            TooBigUsernameError: status.HTTP_400_BAD_REQUEST,
            TooSmallUsernameError: status.HTTP_400_BAD_REQUEST,
            UsernameCantBeEmptyError: status.HTTP_400_BAD_REQUEST,
            BadUsernameError: status.HTTP_400_BAD_REQUEST,
            WrongUserEmailFormatError: status.HTTP_400_BAD_REQUEST,
            WeakPasswordWasProvidedError: status.HTTP_400_BAD_REQUEST,
            PasswordCantBeEmptyError: status.HTTP_400_BAD_REQUEST,
            CardQuestionEmptyError: status.HTTP_400_BAD_REQUEST,
            TooShortQuestionError: status.HTTP_400_BAD_REQUEST,
            TooLongQuestionError: status.HTTP_400_BAD_REQUEST,
            CardAnswerEmptyError: status.HTTP_400_BAD_REQUEST,
            TooLongAnswerError: status.HTTP_400_BAD_REQUEST,
            TooShortAnswerError: status.HTTP_400_BAD_REQUEST,
            EmptyCardTagError: status.HTTP_400_BAD_REQUEST,
            TooLongCardTagError: status.HTTP_400_BAD_REQUEST,
            DuplicateCardTagError: status.HTTP_400_BAD_REQUEST,
            TooShortCardTagError: status.HTTP_400_BAD_REQUEST,
            DeckTitleEmptyError: status.HTTP_400_BAD_REQUEST,
            DeckConfigNameEmptyError: status.HTTP_400_BAD_REQUEST,
            NewGreaterThanReviewedError: status.HTTP_400_BAD_REQUEST,
            TooBigCardLimitError: status.HTTP_400_BAD_REQUEST,
            TooSmallCardLimitError: status.HTTP_400_BAD_REQUEST,
            LearningIntervalGreaterGraduatingError: status.HTTP_400_BAD_REQUEST,
            NotEnoughLearningStepsError: status.HTTP_400_BAD_REQUEST,
            TooLowStepIntervalError: status.HTTP_400_BAD_REQUEST,
            TooSmallLeechThresholdError: status.HTTP_400_BAD_REQUEST,
            TooSmallMinRepeatIntervalError: status.HTTP_400_BAD_REQUEST,
            TooLowMaxIntervalError: status.HTTP_400_BAD_REQUEST,
            TooLowEasyFactorError: status.HTTP_400_BAD_REQUEST,
            InvalidIntervalModifierError: status.HTTP_400_BAD_REQUEST,
            HardIntervalNotLessThanEaseFactorError: status.HTTP_400_BAD_REQUEST,
            InvalidNewIntervalError: status.HTTP_400_BAD_REQUEST,
            TooLowEaseFactorError: status.HTTP_400_BAD_REQUEST,
            TooLowIntervalError: status.HTTP_400_BAD_REQUEST,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            SortingError: status.HTTP_400_BAD_REQUEST,
            # 401
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            # 403
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            NoPermissionToManageUserError: status.HTTP_403_FORBIDDEN,
            RoleAssignmentNotPermittedError: status.HTTP_403_FORBIDDEN,
            RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
            AccessChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
            # 404
            UserNotFoundByEmailError: status.HTTP_404_NOT_FOUND,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            DeckNotFoundError: status.HTTP_404_NOT_FOUND,
            DeckConfigNotFoundError: status.HTTP_404_NOT_FOUND,
            CardNotFoundError: status.HTTP_404_NOT_FOUND,
            CardProgressNotFoundError: status.HTTP_404_NOT_FOUND,
            CardTagNotFoundError: status.HTTP_404_NOT_FOUND,
            # 409
            AlreadyAuthenticatedError: status.HTTP_409_CONFLICT,
            UserAlreadyExistsError: status.HTTP_409_CONFLICT,
            EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
            DeckConfigInUseError: status.HTTP_409_CONFLICT,
            # 503
            GatewayError: status.HTTP_503_SERVICE_UNAVAILABLE,
            EntityAddError: status.HTTP_503_SERVICE_UNAVAILABLE,
            RollbackError: status.HTTP_503_SERVICE_UNAVAILABLE,
            InfrastructureError: status.HTTP_503_SERVICE_UNAVAILABLE,
        }
    )

    def __init__(self, app: FastAPI) -> None:
        self._app: Final[FastAPI] = app
        self._internal_server_error: Final[int] = 500

    async def _handle(self, _: Request, exc: Exception) -> JSONResponse:
        status_code: int = self._ERROR_MAPPING.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

        response: ExceptionSchema | ExceptionSchemaRich
        if isinstance(exc, pydantic.ValidationError):
            response = ExceptionSchemaRich(str(exc), jsonable_encoder(exc.errors()))
        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            message_if_unavailable: str = "Service temporary unavailable. Please try later."
            response = ExceptionSchema(message_if_unavailable)
        else:
            message: str = str(exc) if status_code < self._internal_server_error else "Internal server error"
            response = ExceptionSchema(message)

        return JSONResponse(content=jsonable_encoder(response), status_code=status_code)

    def setup_exception_handlers(self) -> None:
        for exc_class in self._ERROR_MAPPING:
            self._app.add_exception_handler(exc_class, self._handle)
        self._app.add_exception_handler(Exception, self._handle)
