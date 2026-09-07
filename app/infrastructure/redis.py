from redis import Redis

from app.core.config import get_settings


def build_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=False)


def check_redis() -> None:
    build_redis().ping()
