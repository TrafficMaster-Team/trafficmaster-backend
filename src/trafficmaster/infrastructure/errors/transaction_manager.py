from trafficmaster.infrastructure.errors.base import InfrastructureError


class EntityAddError(InfrastructureError): ...


class RollbackError(InfrastructureError): ...
