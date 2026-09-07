from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/readinessProb")
def readiness() -> dict:
    return {"code": 0, "msg": "success", "data": {"ready": True}}
