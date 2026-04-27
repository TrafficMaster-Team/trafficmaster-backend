from trafficmaster.domain.common.errors import DomainError


class WeakPasswordWasProvidedError(DomainError): ...


class EmptyPasswordWasProvidedError(DomainError): ...


class PasswordCantBeEmptyError(DomainError): ...
