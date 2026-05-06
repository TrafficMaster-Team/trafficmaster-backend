from trafficmaster.application.errors.base import ApplicationError


class UserNotFoundByEmailError(ApplicationError): ...


class UserAlreadyExistsError(ApplicationError): ...
