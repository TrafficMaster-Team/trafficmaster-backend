from typing import Any, Final, Literal, NewType, TypedDict, cast

import jwt

from trafficmaster.application.auth.auth_model import AuthSession

JwtSecret = NewType("JwtSecret", str)

JwtAlgorithm = Literal["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]


class JwtPayload(TypedDict):
    auth_session_id: str
    exp: int


class JwtAccessTokenProcessor:
    def __init__(self, jwt_secret: JwtSecret, jwt_algorithm: JwtAlgorithm) -> None:
        self._jwt_secret: Final[JwtSecret] = jwt_secret
        self._jwt_algorithm: Final[JwtAlgorithm] = jwt_algorithm

    def encode(self, auth_session: AuthSession) -> str:
        payload: JwtPayload = JwtPayload(auth_session_id=auth_session.id_, exp=int(auth_session.expiration.timestamp()))

        return jwt.encode(cast("dict[str, Any]", payload), self._jwt_secret, algorithm=self._jwt_algorithm)

    def decode_auth_session_id(self, jwt_token: str) -> str | None:

        try:
            payload: dict[str, Any] = jwt.decode(jwt_token, self._jwt_secret, algorithms=[self._jwt_algorithm])

        except jwt.PyJWTError:
            return None

        return payload.get("auth_session_id")
