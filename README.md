# llm-wiki-server 文档体系 v4

> 文档状态：Draft / Design Baseline  
> 版本：v4  
> 日期：2026-09-07

## 文档地图

| 编号 | 文档 | 回答的问题 |
|---|---|---|
| 01 | [重构方案](./01-refactoring-plan.md) | Why / What：为什么重构、重构什么、不重构什么 |
| 02 | [架构与技术设计](./02-architecture-design.md) | How：系统如何组成、数据如何流动、关键技术决策 |
| 03 | [API 设计](./03-api-design.md) | Contract：REST/MCP 对外契约 |
| 04 | [数据模型与存储设计](./04-data-design.md) | Data Contract：MySQL/ES/OBS/Repository |
| 05 | [实施与部署计划](./05-deployment-plan.md) | When / Where / Gate：怎么实施、测试、部署、上线 |
| 06 | [测试与验收方案](./06-test-acceptance.md) | Proof：如何证明功能、质量、可靠性达标 |

## 依赖关系

```text
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
```

## 设计原则

1. `t_task` 是异步任务事实源，Kafka 是 delivery mechanism。
2. MySQL/OBS 保存 canonical state；ES、Graph、Redis 是 derived projection/cache。
3. REST `search` 负责 discovery；`read` 负责 authoritative retrieval；服务端不提供问答。
4. 图谱显式链接与语义推断边分离，并保留 edge_type/confidence/provenance。
5. CAS 乐观锁解决并发写，不等于历史能力；revision/history 必须独立设计。
6. 不机械进行 TypeScript → Python 翻译，而是迁移行为：characterization tests → domain model → Python implementation。
7. 所有核心能力都需要 golden dataset / golden tests。
8. 第一版优先保证多项目、多用户、可恢复、可观测和可重建。
