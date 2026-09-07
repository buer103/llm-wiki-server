# llm-wiki-server API 设计 v4

## 1. 基础约定

Base URL：`/v1/llm-wiki-server`

- JSON 字段：snake_case
- 时间戳：UTC bigint milliseconds
- path version：`v1`
- 成功：`{"code":0,"msg":"success","data":{}}`
- 错误：`{"code":409,"msg":"conflict","error_code":"WIKI.502"}`
- 分页：`page/page_size`

## 2. 鉴权

- 人机：VIAM Bearer
- 机机：AppToken
- 所有 project API 必须执行 `project_guard`
- project scope 是权限边界，不允许只依赖请求参数。

## 3. Health

`GET /v1/health/readinessProb`

用于 readiness，不代表完整业务健康。

## 4. Project API

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`
- `GET /projects/{project_id}/purpose`
- `GET /projects/{project_id}/schema`
- `GET /projects/{project_id}/members`
- `POST /projects/{project_id}/import`
- `POST /projects/{project_id}/export`
- `POST /projects/{project_id}/reindex`
- `POST /projects/{project_id}/dedup`

长耗时操作返回 `task_id`。

## 5. Source API

支持：upload、list、tree、detail、delete、rescan。

### URL Import 决策

`import-url` 不实现，API contract 不再暴露该端点。

`clip` 保留，作为显式用户行为来源。

## 6. Task API

- `GET /tasks/{task_id}`
- `GET /tasks`
- `POST /tasks/{task_id}/retry`
- `POST /tasks/{task_id}/cancel`

状态：`pending -> running -> done|failed|cancelled`。

retry ≤ 3。

## 7. Search API

核心：`POST /projects/{project_id}/search`

请求：

```json
{
  "query": "string",
  "mode": "hybrid",
  "retrieval_mode": "balanced",
  "top_k": 20,
  "max_tokens": 8000,
  "include_graph": true,
  "include_images": false,
  "filters": {},
  "highlight": true
}
```

响应：

```json
{
  "pages": [],
  "sources": [],
  "graph": [],
  "budget": {"used_tokens": 0, "max_tokens": 8000},
  "degraded": false
}
```

vector 不可用时 `degraded=true`，并以 BM25 作为降级路径。

### Evidence Contract

统一表达：
- evidence_id
- type: page/source/media/graph
- project_id
- source/page identity
- title/path
- content/snippet
- score
- retrieval_signals
- provenance
- relations

### Discovery vs Read

Search = discovery；Read = authoritative retrieval。

建议：
- `GET /projects/{project_id}/pages/{page_id}`
- `GET /projects/{project_id}/sources/{source_id}`

## 8. Page API

- tree
- get
- `PUT /pages/{page_id}`：CAS
- embed

CAS 冲突返回 conflict；CAS 不等于 revision/history。

## 9. Graph API

- graph
- insights
- dismiss

Graph response 必须区分 explicit edges 与 inferred edges。

## 10. Review / Research / Lint

Review：list、resolve、dismiss、batch research。

Research：topic、confirm、reject、list。

Lint：执行与结果查询。

## 11. Clip / Export / Options / Admin

保留 Chrome Clip、Obsidian Export、project export、options 等能力；Admin 工具与 Consumer 工具在 MCP 层分组。

## 12. MCP

第一阶段优先 Consumer tools：search/read/list/tree 等；第二阶段 Admin tools：ingest/reindex/review/research/export 等。

MCP 不替代 REST contract，所有 project-scoped 操作仍遵循统一鉴权和权限模型。
