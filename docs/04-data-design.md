# llm-wiki-server 数据模型与存储设计 v4

## 1. 总体原则

- UUID varchar(36) 主键。
- UTC bigint milliseconds。
- utf8mb4。
- OrderedJSON TypeDecorator → LONGTEXT。
- status 做软删除/状态控制。
- MySQL/OBS 是 canonical；ES/Graph/Redis 是 derived。

## 2. MySQL 表

核心 9 表：
1. `t_project`
2. `t_project_member`
3. `t_source`
4. `t_wiki_page`
5. `t_page_link`
6. `t_media`
7. `t_task`
8. `t_review_item`
9. `t_research_topic`

## 3. ER

```text
project
├── members
├── sources ──< media
├── wiki_pages ──< page_links
├── tasks
├── review_items
└── research_topics
```

## 4. t_project

核心：id、name、description、template、language、owner_id、purpose_md、schema_md、settings、status。

settings 白名单：
- llm_model
- timeout
- context_window
- vector
- reasoning
- pdf_backend
- media_caption
- dedup_auto
- dismissed_insights
- history_size

API 与 Data Design 必须共享这份白名单定义。

## 5. t_project_member

- project_id
- user_id
- role: owner/editor/reader

唯一键：`(project_id, user_id)`。

## 6. t_source

核心：obs_key、parsed_obs_key、filename、folder_path、format、file_size、content_sha256、origin、source_url、title、ingest_status、last_error、last_task_id。

### URL import 清理

API 已明确 URL batch import 不实现。因此 v4 建议：
- `format` 删除 `url`
- `origin` 删除 `url`
- 保留 `clip`
- 可保留 `research`

如果历史数据已有 URL source，迁移脚本必须先完成兼容清洗。

## 7. t_wiki_page

核心：project_id、path、title、page_type、content、frontmatter、source_ids、token_count、data_version、es_synced、status。

唯一：`(project_id, path)`。

CAS：`data_version` 作为乐观锁。

软删：`{path}#del#{page_id}`，避免 unique 冲突。

`frontmatter.sources` 是语义 canonical relation；`t_wiki_page.source_ids` 是加速 projection，二者必须定义同步规则。

## 8. Revision / History

建议新增 `t_wiki_page_revision`：
- revision_id
- page_id
- revision_no
- content
- frontmatter
- data_version
- created_at
- created_by
- change_reason

唯一：`(page_id, revision_no)`。

用途：回滚、审计、diff、Review、调试 LLM merge。

## 9. t_page_link / Graph edge

`t_page_link`：from_page_id、to_page_id、to_title；支持 ghost link；唯一 `(from_page_id, to_title)`。

Graph projection 增加：
- edge_type: wikilink/source_overlap/semantic_inferred
- confidence
- provenance/source

## 10. t_media

source_id、obs_key、content_sha256、page_no、width、height、caption、alt_text、language。

## 11. t_task

任务事实源。

类型：ingest/research/lint/export/import/reindex/embed/dedup。

状态：pending/running/done/failed/cancelled。

核心：progress、request_input、result、error、retry_count、source、heartbeat、timeout、started_at、finished_at。

执行前使用 `SELECT ... FOR UPDATE`，然后 CAS 抢占，防止 Kafka at-least-once 导致双执行。

## 12. t_review_item

origin：ingest/lint/dedup。

review_type：contradiction/duplicate/missing-page/suggestion/confirm。

action_type：create_page/deep_research/skip。

包含 payload、search_queries、status、resolution、reviewIdFor；`reviewIdFor` 用于幂等去重。

## 13. t_research_topic

topic、queries、origin、status、task_id、result_page_id。

## 14. Elasticsearch

双索引：`llm_wiki_page`、`llm_wiki_source`。

文本字段使用 IK analyzer；embedding 1024 dimensions。

CSS 7.10.2 实测：`script_score + painless cosine`，不假设标准 kNN。

RRF：Python `rrf_fusion`，`rrf_k=60`。

ES refresh 策略必须在实现文档中固定。

## 15. OBS Key

```text
sources/{source_id}/{filename}
parsed/{source_id}.md
media/{source_id}/img-{n}.png
exports/{project_id}/{task_id}/...
```

## 16. Repository

至少：ProjectRepository、MemberRepository、SourceRepository、WikiPageRepository、PageLinkRepository、MediaRepository、TaskRepository、ReviewRepository、ResearchRepository。

Repository 不承担业务编排。

## 17. Projection Rebuild

```text
MySQL canonical
      |
      +--> rebuild ES page
      +--> rebuild ES source
      +--> rebuild Graph
```

任何 projection 都不能成为唯一事实源。

## 18. Migration

数据库迁移优先：`expand -> deploy -> backfill -> switch -> contract`。

删除 `url` format/origin 前，先完成历史数据迁移。
