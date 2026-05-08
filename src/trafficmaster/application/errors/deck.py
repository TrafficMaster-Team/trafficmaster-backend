from trafficmaster.application.errors.base import ApplicationError


class DeckNotFoundError(ApplicationError): ...


class DeckConfigNotFoundError(ApplicationError): ...


class DeckConfigInUseError(ApplicationError): ...
