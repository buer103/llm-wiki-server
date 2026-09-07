from collections.abc import Callable

from fastapi import APIRouter

from app.infrastructure.db import check_mysql
from app.infrastructure.elasticsearch import check_elasticsearch
from app.infrastructure.http_dependencies import check_litellm, check_obs, check_viam
from app.infrastructure.kafka import check_kafka
from app.infrastructure.redis import check_redis

router = APIRouter(tags=["health"])


@router.get("/health/readinessProb")
def readiness() -> dict:
    return {"code": 0, "msg": "success", "data": {"ready": True}}


@router.get("/health/dependencies")
def dependencies() -> dict:
    checks: dict[str, Callable[[], None]] = {
        "mysql": check_mysql,
        "redis": check_redis,
        "elasticsearch": check_elasticsearch,
        "kafka": check_kafka,
        "obs": check_obs,
        "litellm": check_litellm,
        "viam": check_viam,
    }
    result: dict[str, dict[str, object]] = {}
    for name, check in checks.items():
        try:
            check()
            result[name] = {"ready": True}
        except Exception as exc:
            result[name] = {"ready": False, "error": type(exc).__name__}
    ready = all(item["ready"] for item in result.values())
    return {"code": 0, "msg": "success", "data": {"ready": ready, "dependencies": result}}
