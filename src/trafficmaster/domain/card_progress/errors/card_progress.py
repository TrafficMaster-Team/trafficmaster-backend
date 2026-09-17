from trafficmaster.domain.common.errors import DomainFieldError


class TooLowEaseFactorError(DomainFieldError): ...


class TooHighEaseFactorError(DomainFieldError): ...


class TooLowIntervalError(DomainFieldError): ...
