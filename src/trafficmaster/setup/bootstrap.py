from functools import lru_cache

from trafficmaster.setup.config.settings import AppConfig


@lru_cache(maxsize=1)
def setup_config() -> AppConfig:
    return AppConfig()
