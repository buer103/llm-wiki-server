# llm-wiki-server 文档体系 v4

> 文档状态：Draft / Design Baseline  
> 版本：v4  
> 日期：2026-09-07

本仓库用于将原 `llm-wiki` 重构为公司内部可部署的 Python 知识存储与检索服务。

## 当前状态

- **P0：设计与代码基线文档已合并到 `master`**
- **P1：Python Server Foundation 进行中**
- P1 不实现 Ingest/Search/Graph/Research 业务，只建立可测试的运行时与模块边界。

## 文档地图

| 编号 | 文档 | 回答的问题 |
|---|---|---|
| 00 | [P0 代码基线](./docs/00-p0-code-baseline.md) | 开始编码前，如何固定原版行为与迁移边界 |
| 01 | [重构方案](./docs/01-refactoring-plan.md) | Why / What：为什么重构、重构什么、不重构什么 |
| 02 | [架构与技术设计](./docs/02-architecture-design.md) | How：系统如何组成、数据如何流动、关键技术决策 |
| 03 | [API 设计](./docs/03-api-design.md) | Contract：REST/MCP 对外契约 |
| 04 | [数据模型与存储设计](./docs/04-data-design.md) | Data Contract：MySQL/ES/OBS/Repository |
| 05 | [实施与部署计划](./docs/05-deployment-plan.md) | When / Where / Gate：怎么实施、测试、部署、上线 |
| 06 | [测试与验收方案](./docs/06-test-acceptance.md) | Proof：如何证明功能、质量、可靠性达标 |
| 07 | [Python 开发指南](./docs/07-development-guide.md) | P1 如何启动、分层与验证 |

## 依赖关系

```text
00 P0 Code Baseline
        |
        v
01 Refactoring Plan
        |
        v
02 Architecture & Technical Design
      /   \\
     v     v
03 API   04 Data
      \\   /
        v
05 Implementation & Deployment
        |
        v
06 Test & Acceptance
        |
        v
07 Python Development Guide
```

## P1 代码结构

```text
app/
├── api/             # REST/MCP adapters
├── core/            # configuration and cross-cutting concerns
├── domain/          # business concepts, infrastructure-independent
├── services/        # application use cases
├── repositories/    # persistence abstractions
├── infrastructure/  # MySQL/ES/Redis/Kafka/OBS/LiteLLM/VIAM adapters
└── workers/         # asynchronous task consumers

tests/
├── unit/
├── contract/
├── integration/
└── golden/
```

## 设计原则

1. `t_task` 是异步任务事实源，Kafka 是 delivery mechanism。
2. Source binary 的 canonical state 在 OBS，metadata 在 MySQL；Wiki page canonical state 在 MySQL；ES/Graph/Redis 是 derived projection/cache。
3. REST `search` 负责 discovery；`read` 负责 authoritative retrieval；服务端不提供问答。
4. 图谱显式链接与语义推断边分离，并保留 edge_type/confidence/provenance。
5. CAS 乐观锁解决并发写，不等于历史能力；revision/history 独立设计。
6. 不机械进行 TypeScript → Python 翻译，而是迁移行为：characterization tests → domain model → Python implementation。
7. 所有核心能力都需要 golden dataset / golden tests。
8. 第一版优先保证多项目、多用户、可恢复、可观测和可重建。
9. 每个实施阶段都必须闭环一个可验证的用户价值。
