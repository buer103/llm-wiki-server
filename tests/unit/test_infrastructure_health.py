from fastapi.testclient import TestClient

from app.api.routes import health
from app.main import app


def test_dependency_health_reports_each_adapter(monkeypatch) -> None:
    checks = (
        health.check_mysql,
        health.check_redis,
        health.check_elasticsearch,
        health.check_kafka,
        health.check_obs,
        health.check_litellm,
        health.check_viam,
    )
    for check in checks:
        monkeypatch.setattr(health, check.__name__, lambda: None)

    response = TestClient(app).get("/v1/llm-wiki-server/health/dependencies")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ready"] is True
    assert all(item["ready"] for item in data["dependencies"].values())
