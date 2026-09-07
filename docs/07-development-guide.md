# Python 开发指南

## 目标

P1 建立服务运行、基础设施 adapter 与模块边界，不提前实现业务域。后续实现必须遵循：characterization tests → domain model → implementation。

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

基础设施 smoke：

```text
GET /v1/llm-wiki-server/health/dependencies
```

该接口会逐项检查 MySQL、Redis、Elasticsearch、Kafka、OBS、LiteLLM、VIAM。开发环境未配置的依赖会报告 `ready=false`，不会伪装成已连接。

## 分层规则

- `domain/`：稳定业务概念，不依赖基础设施。
- `services/`：用例编排与事务边界。
- `repositories/`：持久化抽象。
- `infrastructure/`：MySQL/ES/Redis/Kafka/OBS/LiteLLM/VIAM adapter。
- `api/`：REST/MCP adapter，不承载核心业务逻辑。
- `workers/`：异步任务消费；`t_task` 是事实源，Kafka 只负责 delivery。

## Infrastructure rules

1. 应用代码依赖接口，不直接依赖具体 SDK。
2. adapter 负责连接参数、连接池和外部系统协议。
3. smoke check 不读取或返回密码、token、access key 等秘密。
4. Kafka v1 不允许静默 fallback 到进程内队列。
5. MySQL 使用 SQLAlchemy 2 DeclarativeBase；业务同步 DB 操作在服务层通过线程边界隔离。
6. ES 版本固定，索引是 derived projection，不是 canonical state。

## P1 Gate

- 应用可以启动。
- 配置通过环境变量注入。
- readiness contract 有测试。
- 基础设施可以通过接口替换。
- 基础设施依赖均有可执行 adapter/probe。
- 单元、契约、集成、golden 测试目录已建立。
- 不引入生产凭据，不在代码中硬编码密钥。
