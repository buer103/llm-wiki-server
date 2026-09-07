# llm-wiki-server 测试与验收方案 v4

## 1. 测试层级

```text
Unit
 -> Characterization
 -> Contract
 -> Integration
 -> E2E
 -> Failure
 -> Performance
 -> Security
 -> Production rehearsal
```

## 2. Golden Dataset

建立固定数据集：PDF、DOCX、PPTX、XLSX、Markdown、HTML、图片/媒体、中文/英文混合。

每份数据记录 expected pages、expected links、expected source attribution、expected search queries、expected important evidence。

Golden dataset 是后续模型/Prompt/Parser 修改的回归基线。

## 3. Characterization Tests

从原版提取行为：page generation、page merge、source attribution、graph relation、retrieval ranking、token budget。

Python 版本必须先通过行为测试，再接受实现差异。

## 4. API Contract Tests

验证 envelope、error_code、pagination、timestamp、auth、project_guard、CAS conflict、async task response、degraded search。

重点覆盖所有 project-scoped routes。

## 5. Ingest Acceptance

### Source
- 文件上传正确。
- SHA256 正确。
- OBS key 正确。
- parser 输出稳定。

### Wiki
- 页面数量合理。
- source attribution 正确。
- link 正确。
- validator 能拒绝明显错误。
- commit 幂等。

### Projection
- ES 最终可查询。
- ES failure 可重试。
- reindex 可恢复。

## 6. Search Acceptance

固定 query 集合验证 BM25、vector、RRF、graph expansion、filters、highlight、max_tokens、include_images、faithful mode。

必须验证 result provenance、source/page relation，以及 degraded=true 时仍可用。

## 7. Graph Acceptance

验证 explicit edge、ghost link、inferred edge、edge_type、confidence、Louvain、insight、dismiss、rebuild。

## 8. Task / Kafka Acceptance

必须测试：
1. Kafka at-least-once。
2. 同一 task 重复 delivery。
3. worker crash after claim。
4. heartbeat timeout。
5. retry ≤ 3。
6. task cancellation。
7. Kafka unavailable fallback。
8. 同 project 并发 ingest。

验收要求：不产生重复最终页面；task state 可解释；stuck task 可恢复。

## 9. Failure Matrix

| Failure | Expected |
|---|---|
| MySQL down | API 明确失败，不写半状态 |
| OBS down | source task failed/retry |
| ES down | canonical write 仍可完成；projection retry |
| Kafka down | 按环境策略 fallback |
| LLM 429 | retry/backoff |
| LLM malformed | validator + retry/review |
| Worker crash | heartbeat recovery |
| duplicate task | idempotent |
| vector unavailable | BM25 degraded |
| CAS conflict | 409/WIKI conflict |
| Pod restart | task recover |
| ES index corrupt | rebuild |

## 10. Revision / History Acceptance

必须能保存 revision、查询历史、diff、rollback，并在 rollback 后重建 ES projection。

## 11. Performance

目标在 staging 根据实际容量基线压测。

至少测 search p50/p95/p99、upload latency、ingest throughput、LLM concurrency、ES query latency、Kafka lag、worker throughput。

不得只测试单副本。

## 12. Security

- 未认证请求拒绝。
- project 越权拒绝。
- reader/editor/owner 权限符合定义。
- AppToken scope 正确。
- Secrets 不进入日志。
- CORS 生产受限。
- source/page content 不通过错误响应泄漏。

## 13. Production Rehearsal

上线前演练 pod kill、worker crash、Kafka outage、ES outage、MySQL transient failure、LLM 429、task retry、ES rebuild、rollback、database migration。

## 14. Release Acceptance Checklist

### Functional
- [ ] Project
- [ ] Source
- [ ] Ingest
- [ ] Wiki
- [ ] Search
- [ ] Graph
- [ ] Review
- [ ] Research
- [ ] Lint
- [ ] MCP
- [ ] Clip
- [ ] Export

### Reliability
- [ ] Task recovery
- [ ] Kafka duplicate delivery
- [ ] ES rebuild
- [ ] Revision/history
- [ ] Multi-replica concurrency

### Security
- [ ] VIAM
- [ ] AppToken
- [ ] project_guard
- [ ] restricted CORS
- [ ] externalized secrets

### Operations
- [ ] Metrics
- [ ] Logs
- [ ] Alerts
- [ ] Dashboard
- [ ] Runbook
- [ ] Rollback rehearsal
