from fastapi.testclient import TestClient

from app.main import app


def test_readiness_contract() -> None:
    response = TestClient(app).get("/v1/llm-wiki-server/health/readinessProb")
    assert response.status_code == 200
    assert response.json() == {"code": 0, "msg": "success", "data": {"ready": True}}
