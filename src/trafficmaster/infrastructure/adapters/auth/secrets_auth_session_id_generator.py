import secrets
from typing import override

from trafficmaster.application.common.ports.auth.id_generator import AuthIDGenerator


class SecretsAuthSessionIdGenerator(AuthIDGenerator):
    @override
    def __call__(self) -> str:
        return secrets.token_urlsafe(32)
