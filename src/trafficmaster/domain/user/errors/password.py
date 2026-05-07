from trafficmaster.domain.common.errors import DomainError


class WeakPasswordWasProvidedError(DomainError): ...


class PasswordCantBeEmptyError(DomainError): ...
