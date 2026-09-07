# P0：代码基线与能力矩阵

> 目标：在开始 TypeScript → Python 迁移前，固定原版行为、边界和依赖，避免“重构”过程中无意改变产品语义。

## 1. P0 输出物

- 原版运行基线：启动方式、环境变量、数据库/ES/OBS/Kafka 等依赖。
- 功能能力矩阵：原版能力 → Server v1 保留/删除/替代。
- 路由矩阵：UI/API/Agent/MCP 调用点 → 新 REST/MCP contract。
- 数据模型矩阵：前端/服务端现有实体 → MySQL canonical model。
- Characterization tests：固定关键行为，不追求测试旧实现内部结构。
- Golden Dataset：用于 ingest/search/graph 的稳定样本。
- 风险清单：高风险迁移点及对应验证方法。

## 2. 能力迁移原则

| 原能力 | Server v1 | 处理方式 |
|---|---|---|
| Wiki 页面管理 | 保留 | REST + MySQL canonical + ES projection |
| 文件上传/解析 | 保留 | OBS + ingest pipeline |
| 两阶段 LLM ingest | 保留 | Python domain/service 重建 |
| 混合检索 | 保留 | BM25 + vector + RRF + graph expansion |
| Graph / Louvain / insights | 保留 | 独立 graph service/domain |
| Deep Research | 保留 | provider interface + async task |
| Review / lint | 保留 | task + review item |
| Obsidian export | 保留 | async export task |
| URL 批量导入 | 删除 | 不进入 v1 contract |
| Agent Chat / Q&A | 删除 | Agent 自己完成 answer synthesis |
| Agent Runtime / shell approval | 删除 | 不属于知识服务职责 |
| Workspace / skills runtime | 删除 | 不属于 v1 Server |
| Chrome Clip | 保留 | 作为增长能力，按阶段接入 |

## 3. 行为基线

### 3.1 Ingest

必须固定：

1. 文件解析后的 canonical text。
2. LLM analyze 输出的结构约束。
3. page generate 的标题、path、frontmatter 和 links 规则。
4. validation 失败时的行为。
5. page merge / overwrite / conflict 行为。
6. commit 后 ES projection 的字段。
7. 相同 source 重复 ingest 的幂等语义。

### 3.2 Search

必须固定：

1. BM25 检索结果排序。
2. vector 检索结果排序。
3. RRF 融合行为。
4. graph expansion 的四类 signal。
5. top_k / max_tokens budget 截断行为。
6. filter 语义。
7. highlight 结构。
8. vector 不可用时 degraded=true 的行为。

### 3.3 Graph

必须固定：

- page-link 显式边。
- 语义推断边。
- edge_type / confidence / provenance。
- Louvain community。
- insights / surprising connections / knowledge gaps。

## 4. Golden Dataset

建议至少包含：

- 10 个小型 Markdown 文档。
- 5 个真实复杂 Markdown/Wiki 文档。
- PDF / DOCX / PPTX / XLSX 各至少 1 个。
- 含图片和表格的文档。
- 含重复内容的 source。
- 含 broken/ghost link 的 Wiki。
- 中英文混合检索样本。
- 至少 20 个固定 search queries。
- 至少 5 个 graph insight 场景。

每个样本记录：

```text
sample_id
source_file
expected_page_count
expected_titles
expected_links
expected_media_count
expected_search_hits
expected_graph_edges
```

## 5. Characterization Test 分层

```text
L0  Pure function / parser behavior
L1  Domain behavior
L2  API contract
L3  Search ranking / retrieval
L4  Ingest E2E
L5  Infrastructure integration
```

迁移顺序：先建立测试，再实现 Python；测试只描述用户可观察行为或稳定领域规则。

## 6. P0 Gate

只有满足以下条件，才能进入 P1/P2：

- [ ] 原版可以重复启动并运行核心流程。
- [ ] 依赖版本和配置已记录。
- [ ] 能力矩阵完成并经过评审。
- [ ] v1 删除项没有隐藏调用方。
- [ ] Golden Dataset 固化。
- [ ] 核心 ingest/search/graph characterization tests 固化。
- [ ] 所有高风险迁移点有验证计划。

## 7. P0 不做什么

P0 不实现 Python Server，不迁移业务代码，不部署生产 K8s；只建立可验证的行为和迁移边界。