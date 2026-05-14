from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.infrastructure.errors.base import InfrastructureError


class EntityAddError(GatewayError): ...


class RollbackError(InfrastructureError): ...
