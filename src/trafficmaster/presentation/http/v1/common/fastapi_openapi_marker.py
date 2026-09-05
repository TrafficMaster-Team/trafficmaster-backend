from fastapi.security import APIKeyCookie

from trafficmaster.presentation.http.v1.common.auth_cookie import ACCESS_TOKEN_COOKIE_KEY

cookie_scheme = APIKeyCookie(name=ACCESS_TOKEN_COOKIE_KEY)
