from trafficmaster.application.errors.base import ApplicationError


class AuthenticationError(ApplicationError): ...


class AlreadyAuthenticatedError(ApplicationError): ...


class AuthorizationError(ApplicationError): ...
