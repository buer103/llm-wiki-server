# llm-wiki-server 架构与技术设计 v4

## 1. 总体架构

```text
Client / Agent / MCP
        |
     Ingress
        |
     FastAPI API
        |
   Project / Source / Search / Page / Graph / Research
        |
   +----+---------+----------------+
   |              |                |
 MySQL           OBS              Redis
   |                               |
   +---------- Task State ---------+
                  |
                Kafka
             /          \\
        normal worker   slow worker
             |
    ingest/research/lint/export/embed
             |
      LLM / Embedding / VLM / Search
             |
             +----> Elasticsearch
             +----> Graph projection
```

## 2. 部署形态

K8s namespace：`ics`

最终建议拆成：
- `llm-wiki-api`
- `llm-wiki-worker`
- `llm-wiki-worker-slow`

基础设施：
- MySQL
- Elasticsearch 8.19.2
- Kafka
- OBS
- Redis
- LiteLLM gateway
- Embedding
- VLM
- Web Search
- VIAM

## 3. 技术栈

- Python 3.11
- FastAPI 0.135.1
- uvicorn 0.44.0
- SQLAlchemy 2.0.44
- pymysql 1.1.2
- Elasticsearch client 8.19.2
- kafka-python 2.3.2
- OBS SDK 3.25.3
- OpenAI SDK 2.35.0 → LiteLLM
- MCP 1.28.1 / FastMCP
- networkx
- PyMuPDF / python-docx / python-pptx / openpyxl / ebooklib / mobi / pandas
- httpx / readability-lxml / Firecrawl

数据库使用同步 SQLAlchemy；服务层使用 `asyncio.to_thread` 隔离阻塞 DB I/O。

## 4. 服务分层

```text
routers/
services/
domain/
repositories/
models/
infra/
workers/
pipelines/
```

### Router
只处理 HTTP/MCP contract、鉴权、参数校验和 response mapping。

### Service
承载业务用例与事务边界。

### Repository
封装 MySQL/OBS/ES 等访问。

### Pipeline
承载 ingest/search/research 等编排。

## 5. Ingest Pipeline

```text
upload
 -> OBS raw
 -> parse
 -> normalized content
 -> analyze
 -> generate
 -> validate
 -> merge
 -> commit MySQL
 -> projection ES
 -> graph update
```

M2 必须拆解：
- M2-A LLM Client
- M2-B Prompt
- M2-C Validator
- M2-D Page Merge
- M2-E Commit
- M2-F ES Projection
- M2-G E2E

## 6. Search Pipeline

```text
query
 -> permission/project scope
 -> BM25
 -> vector
 -> RRF
 -> graph expansion
 -> token budget
 -> evidence normalization
 -> response
```

Search response 使用统一 Evidence contract，使 page/source/media/graph relation 可被 Agent 直接消费。

`faithful` 模式只返回可追溯 sources；vector 不可用时返回 `degraded=true`。

## 7. Graph

图谱分为：
- explicit edge：WikiLink / source relation
- semantic inferred edge：LLM/embedding 推断

边至少保存：
- edge_type
- confidence
- source
- created_at

支持：
- Louvain community
- surprising connections
- knowledge gaps
- dismissed insights

## 8. ES

两个 projection：
- `llm_wiki_page`
- `llm_wiki_source`

embedding：
- dimension 1024

CSS 7.10.2 实测路径使用 `script_score + painless cosine`，不假定标准 kNN。

RRF：
- Python `rrf_fusion`
- `rrf_k=60`

ES 必须允许从 MySQL canonical state rebuild。

## 9. 多租户

第一版数据库可以不建立 Tenant 表，但架构层保留：

```text
Tenant / Organization
        |
      Project
        |
   Member / Source / Wiki
```

所有 query 必须先经过 project scope 与权限过滤。

## 10. 一致性

### Write path

```text
MySQL commit
 -> task/project state
 -> Kafka delivery
 -> ES projection
```

projection failure 不回滚 canonical state；通过任务重试/reindex 恢复。

### Idempotency

所有异步任务都应有：
- task_id
- retry_count
- heartbeat
- timeout
- idempotent key / reviewIdFor

## 11. 安全

- 人机 VIAM Bearer。
- 机机 AppToken。
- project_guard。
- Secrets 外置。
- 生产 CORS 禁止默认 `*`。
- 日志不得泄漏 token、原文敏感内容。
- 所有 project-scoped API 必须有统一 auth gate。

## 12. 可观测性

指标至少覆盖：
- API QPS / latency / 5xx
- ingest success/failure
- task pending/running/failed
- Kafka lag
- LLM latency/429
- ES latency/error
- MySQL error
- OBS error
- es_synced backlog
- worker heartbeat timeout
- Pod restart
