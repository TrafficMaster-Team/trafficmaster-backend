from typing import Final

from fastapi import Response

DEFAULT_CACHE_CONTROL: Final[str] = "no-store"
PUBLIC_CACHE_CONTROL: Final[str] = "public, max-age=60"


def enable_public_cache(response: Response) -> None:
    response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
