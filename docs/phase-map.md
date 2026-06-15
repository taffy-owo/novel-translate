# 里程碑落地映射

把研究报告（`deep-research-report.md`）的 8 个月里程碑映射到当前代码：已落地 vs 留接口/TODO。当前完成的是**完整骨架 + 一条端到端 walking skeleton**（报告第 4 到 8 个月的高级能力多为留桩）。

## 已落地（T1–T6）

| 报告阶段 / 能力 | 落地 | 位置 |
|---|---|---|
| 基础设施与导入 (b) | docker-compose(pgvector/redis/minio)、项目/章节、TXT 导入与分段 | `docker-compose.yml`、`modules/projects`、`modules/ingest` |
| 模型路由与分段翻译 (c) | Provider 双通道适配 + registry、统一 TranslateSegmentRequest、arq 任务队列、分段翻译、错误隔离 | `modules/providers/*`、`modules/translation/*`、`worker/*` |
| 编辑器与章节管理 (b3/e1) | 原文/译文对照、逐段编辑、翻译进度轮询 | `apps/desktop/src/pages/*`、`api/hooks.ts` |
| 章节导出 (e3) | 章节 TXT 导出 | `modules/exports/chapter.py`、`GET /chapters/{id}/export` |
| 存储/向量 | PostgreSQL + pgvector，术语表与记忆快照表（含 `Vector(1536)`）落表 | `modules/glossary/models.py`、`modules/memory/models.py`、迁移 `202606150002` |
| 桌面壳 (f3 部分) | Tauri 2 + 原生文件对话框 + read_text_file 命令 | `apps/desktop/src-tauri/*` |
| 术语表 + 术语注入 (d1) | 术语 CRUD + 审批流(draft→approved→deprecated) + 基线候选抽取(频次/重复跨度) + 已审批且命中本段的术语注入翻译请求 | `modules/glossary/*`、`api/v1/glossary.py`、`modules/translation/request.py` |

## 留接口 / TODO（后续阶段）

| 报告阶段 / 能力 | 当前状态 | 落点 |
|---|---|---|
| 术语抽取增强 (d1) | 基线频次/重复跨度抽取已实现；NER/规则增强版为后续 | `modules/glossary/service.py` |
| 分层记忆快照生成 (d2) | 表已建；`build_snapshot` 抛 NotImplementedError | `modules/memory/snapshot.py` |
| 记忆检索（pgvector 近邻） (d2) | `retrieve_memory_hits` 返回 []（管线可无脑调用） | `modules/memory/retrieval.py` |
| 全局一致性校正 (d3) | 翻译响应已含 new_term_candidates/consistency_warnings/summary_delta 字段，逻辑未实现 | `modules/translation/schemas.py` |
| 风格/记忆注入翻译请求 | `glossary_terms` 已注入（见上）；`style_guide`/`memory_hits` 仍为空/None | `modules/translation/request.py` |
| DOCX/EPUB 导入、整书构建 (b2/e4) | 未做（仅 TXT） | 新增 `modules/ingest/{epub,docx}.py`、`exports/project_zip.py` |
| 审校/软锁/版本历史 (e1/e2) | Segment.status/error 字段已预留 | `modules/projects/models.py` |
| Batch API / Prompt Caching | adapter 为同步单条调用 | `modules/providers/*` |
| RLS/RBAC、审计、OpenTelemetry、桌面签名打包 (f1/f3) | 未做；config 留扩展位 | `core/config.py`、CI |
| 对象存储接入导出物 | MinIO 在 compose 内起好，导出暂走 API 直接返回 | `core`（预留 storage） |

## 测试与验证现状

- 后端 `pytest` 20 项全绿（projects CRUD、分段、provider 适配 mock、章节导出、worker 任务 pending→done/error、入队端点、pgvector 嵌入往返、术语 CRUD/审批/基线抽取、术语注入翻译请求）。
- `alembic upgrade head` 至 `202606150002`，建出 6 张表。
- 前端 `pnpm --filter desktop build`（tsc+vite）通过；`cargo check`（src-tauri）通过。
- 未做：真实模型端到端翻译（需配置 Ollama/API key）与 `tauri dev` GUI 实跑（需桌面环境）。
