from fastapi.security import APIKeyCookie

cookie_scheme = APIKeyCookie(name="access_token")
