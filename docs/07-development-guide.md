# Python 开发指南

## 目标

P1 只建立服务运行与模块边界，不提前实现业务域。后续实现必须遵循：characterization tests → domain model → implementation。

## 本地运行

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Readiness：

```text
GET /v1/llm-wiki-server/health/readinessProb
```

## 分层规则

- `domain/`：稳定业务概念，不依赖基础设施。
- `services/`：用例编排与事务边界。
- `repositories/`：持久化抽象。
- `infrastructure/`：MySQL/ES/Redis/Kafka/OBS/LiteLLM/VIAM adapter。
- `api/`：REST/MCP adapter，不承载核心业务逻辑。
- `workers/`：异步任务消费；`t_task` 是事实源，Kafka 只负责 delivery。

## P1 Gate

- 应用可以启动。
- 配置通过环境变量注入。
- readiness contract 有测试。
- 基础设施可以通过接口替换。
- 单元、契约、集成、golden 测试目录已建立。
- 不引入生产凭据，不在代码中硬编码密钥。
