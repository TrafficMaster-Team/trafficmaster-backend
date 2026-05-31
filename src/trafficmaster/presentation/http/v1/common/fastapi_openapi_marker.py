from fastapi.security import APIKeyCookie

from trafficmaster.infrastructure.adapters.auth.constraints import ACCESS_TOKEN_COOKIE_KEY

cookie_scheme = APIKeyCookie(name=ACCESS_TOKEN_COOKIE_KEY)
