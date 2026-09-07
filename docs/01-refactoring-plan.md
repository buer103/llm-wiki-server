# llm-wiki-server 重构方案 v4

## 1. 背景

原项目是基于 Tauri v2 + React 的桌面应用，包含 UI、Agent Runtime、知识库构建、检索、图谱、Deep Research 等能力。

目标是将其重构为公司内部可部署的 Python 知识库存储与检索服务，使知识库能力成为可被其他 Agent、业务系统和工具复用的基础服务。

参考代码：
- 原版参考仓库：`D:\\workspace\\yw_codehub\\llm_wiki\\temp_clone`
- `temp_clone_py` 仅用于吸收生产实践，不作为代码基座。

目标仓库：`buer103/llm-wiki-server`

## 2. 产品定位

### 2.1 做什么

- 多用户、多项目知识库存储。
- 文档摄入、解析、Wiki 生成与校验。
- BM25 + 向量 + RRF 混合检索。
- 图谱扩展与知识洞察。
- Review / Lint。
- Deep Research。
- Chrome Clip / Obsidian Export。
- REST + MCP 消费接口。
- K8s + Kafka worker 化部署。

### 2.2 明确不做

- 不迁移原版 Chat UI。
- 不迁移 Agent Runtime。
- 不迁移 skills/workspace/shell approval。
- 不提供服务端问答 API。
- 不让服务端替调用方完成最终回答。
- 不实现 URL 批量导入；`import-url` 端点废弃。
- 不把 `temp_clone_py` 当作代码基座。

## 3. 核心用户闭环

```text
上传 Source
  -> OBS 原始文件
  -> Parser
  -> LLM Analyze
  -> LLM Generate
  -> Validate
  -> Wiki Page
  -> MySQL canonical
  -> ES projection
  -> Graph projection
  -> Search
  -> Agent 自己读取证据并生成答案
```

## 4. 核心能力边界

| 能力 | Server | 调用方 |
|---|---:|---:|
| 文档存储 | ✓ | |
| 文档解析 | ✓ | |
| Wiki 生成 | ✓ | |
| 混合检索 | ✓ | |
| Graph 扩展 | ✓ | |
| Deep Research | ✓ | |
| Review/Lint | ✓ | |
| 最终问答 | | ✓ |
| Agent Runtime | | ✓ |
| Chat UI | | ✓ |

## 5. 关键架构原则

### 5.1 Canonical vs Derived

- Source binary：OBS canonical。
- Source metadata：MySQL canonical。
- Wiki page：MySQL canonical。
- ES：derived projection，可重建。
- Graph：derived projection，可重建。
- Redis：cache/rate-limit，非事实源。

### 5.2 异步任务

`t_task` 是任务事实源。提交任务先写 MySQL，再投递 Kafka；Kafka 允许 at-least-once delivery。

worker 执行前通过事务锁/状态 CAS 抢占任务，避免重复执行。

如果同一 project 的 ingest 必须串行，Kafka partition key 不足以保证 worker 执行串行，需要额外 project execution lock。

### 5.3 版本与历史

CAS 仅用于防止并发覆盖，不提供历史。

Wiki 必须支持 revision/history，具体实现可以：
- 独立 `t_wiki_page_revision`；或
- 规范化的 OBS page-history。

v4 将 revision/history 视为正式设计项。

## 6. 迁移策略

禁止机械翻译 TS。

每个迁移模块按照：

```text
原版行为分析
 -> characterization test
 -> domain model
 -> Python interface
 -> implementation
 -> golden test
 -> integration test
```

优先迁移：
1. ingest behavior
2. search behavior
3. graph behavior
4. research behavior
5. export/clip

## 7. 里程碑

- M0：代码基线与能力矩阵
- M1：基础设施与 FastAPI 骨架
- M2：Source → Wiki
- M3：Search MVP
- M4：Graph
- M5：Review/Lint
- M6：Deep Research
- M7：MCP
- M8：Clip/Export
- M9：生产可靠性
- M10：灰度上线

## 8. 成功标准

- 能稳定建库。
- 搜索结果可解释、可追溯。
- 服务端不承担最终回答。
- ES 可从 canonical state 重建。
- Kafka 重复投递不会产生错误最终状态。
- 多副本下不会发生同一任务无保护地双执行。
- 具备完整监控、审计、失败恢复和回滚路径。
