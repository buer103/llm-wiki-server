# llm-wiki-server 重构实施与部署计划 v4

## 1. 实施周期

建议完整周期：14–18 周。

不要以“代码行数”作为排期依据；以 capability + acceptance gate 为准。

## 2. Phase

### P0：代码基线
- 固定原版 commit。
- 建立 capability matrix。
- 建立 characterization tests。
- 建立 golden dataset。

### P1：基础设施 PoC
验证 MySQL、ES、Kafka、OBS、Redis、LiteLLM、Embedding、K8s，并完成真实 smoke。

### P2：FastAPI + K8s MVP
project skeleton、health、auth middleware、config、structured logging、metrics、Helm、CI。

### P3：Source → OBS → Parser
upload、OBS、parser、normalized representation、media extraction、task state。

### P4：Source → Wiki
拆分 LLM client、prompt、validator、page merge、commit、ES projection、E2E。

### P5：Search MVP
BM25 → vector → RRF → graph expansion → token budget → Evidence contract。

### P6：Graph
explicit edges、inferred edges、Louvain、insights、dismiss、rebuild。

### P7：Review + Lint
contradiction、duplicate、missing page、suggestion、resolution。

### P8：Deep Research
第一版只要求 provider interface + 一条可工作的 provider。

### P9：MCP
先 consumer tools，再 admin tools。

### P10：Clip / Export
Chrome Clip、Obsidian export、project export。

## 3. 环境

### dev
Kafka disabled、replica=1、本地/共享测试基础设施。

### test
真实 MySQL/ES/OBS/Kafka，集成测试。

### staging
接近生产、replicas ≥ 2、Kafka enabled、完整 observability。

### prod
replicas ≥ 2、Kafka enabled、VIAM enabled、restricted CORS、externalized secrets、limits、PDB、按负载决定 HPA。

## 4. Helm

```text
Chart.yaml
values.yaml
values-test.yaml
values-staging.yaml
values-prod.yaml
templates/
  deployment.yaml
  service.yaml
  configmap.yaml
  secret.yaml
  ingress.yaml
  pdb.yaml
  serviceaccount.yaml
```

## 5. Worker

```text
llm-wiki-api
llm-wiki-worker
llm-wiki-worker-slow
```

Kafka：normal topic、slow topic、独立 consumer group。

## 6. 发布流程

```text
Deploy
 -> Smoke
 -> Internal / Shadow
 -> 10% Canary
 -> 30%
 -> 100%
 -> Observe
```

每一步有明确 rollback gate。

## 7. DB / ES 发布原则

DB：expand → deploy → migrate/backfill → switch → contract。

ES：index versioning → rebuild → alias switch。

## 8. Rollback

API/worker：image rollback。

DB：优先 forward fix，避免 destructive rollback。

ES：rebuild old index，alias switch。

Task：failed task retry、stuck task recovery、manual requeue。

## 9. Gate

1. Infrastructure：真实基础设施全部 smoke pass。
2. Build：Source → Wiki 成功率达标，数据一致。
3. Search：Golden queries 达标，degraded path 可用。
4. Knowledge Growth：Graph/Review/Research 闭环。
5. Production Reliability：多副本、Kafka、恢复、监控通过。
6. Production Launch：灰度成功且 rollback 演练通过。

## 10. 关键风险

| 风险 | 对策 |
|---|---|
| TS→Python 行为漂移 | characterization + golden tests |
| Kafka 重复投递 | t_task + DB CAS/lock |
| 同 project 并发 ingest | project execution lock |
| ES 与 MySQL 不一致 | projection retry/reindex |
| LLM 输出不稳定 | validator + golden dataset |
| 历史无法恢复 | revision/history |
| M2 排期过大 | M2-A~G 拆分 |
| Search 返回不可消费 | Evidence contract |
| 生产 CORS 过宽 | environment-specific config |
