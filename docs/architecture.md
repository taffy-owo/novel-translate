# 架构 (walking skeleton)

novel-translate 是桌面优先的混合架构。本文件描述**当前已落地**的结构（T1–T6），不是完整 8 个月蓝图——后者见 `deep-research-report.md`，里程碑落地映射见 `phase-map.md`。

## 组件

```
┌─────────────────────────────┐        HTTP / JSON           ┌──────────────────────────────┐
│ apps/desktop (Tauri 2)      │  ───────────────────────────▶│ backend: FastAPI (api)         │
│  React 19 + Vite + TS       │   /api/v1/...                │  novel_translate.api.main:app  │
│  react-query 轮询 / zustand │ ◀─────────────────────────── │                                │
│  原生 dialog 选 .txt        │                              └───────────────┬────────────────┘
│  read_text_file(Rust 命令)  │                                              │ enqueue (arq)
└─────────────────────────────┘                                              ▼
                                                              ┌──────────────────────────────┐
   PostgreSQL 17 + pgvector  ◀───────  SQLAlchemy 2.0 async  │ Redis 7  ←  arq 队列            │
   (projects/chapters/segments,        ───────────────────▶  │                                │
    glossary_terms/memory_snapshots)                         │ backend worker:                │
                                                              │  WorkerSettings.translate_     │
   MinIO (S3 兼容, 预留)                                       │  segment → provider 适配 → DB   │
                                                              └──────────────────────────────┘
```

后端是**单 Python 包、双入口**：`uvicorn novel_translate.api.main:app`（API）与 `arq novel_translate.worker.main.WorkerSettings`（worker），共享 `core` / `modules`（models、providers、translation）。

## 模块 (backend/src/novel_translate)

- `api/` — FastAPI 应用与 `v1/` 路由（projects / chapters / segments）+ `deps`（get_session、get_arq_pool）。
- `worker/` — arq `WorkerSettings` + `tasks/translate_segment`（幂等、错误隔离写回 segment）。
- `core/` — `config`（pydantic-settings）、`db`（async engine/session）、`redis`（arq RedisSettings/pool）。
- `modules/projects/` — Project/Chapter/Segment 模型、schema、service。
- `modules/ingest/` — `segment.split_into_segments`（空行分段）、`txt.import_txt_chapter`。
- `modules/providers/` — `base.ProviderAdapter` 抽象 + `openai_compatible` + `anthropic` + `registry.get_provider(kind)`。**新增 provider = 加一个 adapter，不在调用处加 if**。
- `modules/translation/` — `schemas`（TranslateSegmentRequest/Result）、`prompt.build_messages`、`request.build_translate_request`（取相邻段作 local_context）。
- `modules/exports/` — `chapter.export_chapter_txt`。
- `modules/glossary/`、`modules/memory/` — 知识层表（含 `Vector(1536)`）+ 留接口 stub（见 phase-map）。
- `db/` — `base.Base`（统一命名约定）+ Alembic 迁移。

## walking skeleton 数据流

1. 桌面「新建项目」→ `POST /api/v1/projects`。
2. 桌面原生 dialog 选 `.txt` → Rust `read_text_file` 读内容 → `POST /api/v1/projects/{id}/chapters/import-txt` → `import_txt_chapter` 按空行分段建 `Segment(status=pending)`。
3. 桌面「翻译本章」→ `POST /api/v1/chapters/{id}/translate` → 对每个 pending segment `enqueue_job("translate_segment", id)`。
4. worker 取 job → `translate_segment`：status→translating → `build_translate_request`（带前后句）→ `get_provider(kind).translate(req)` → 写回 `target_text` + status=done（失败写 status=error+error，不冒泡）。
5. 桌面 react-query 轮询 `GET /api/v1/chapters/{id}`（有 pending/translating 段时 2s 一次）→ 原文/译文左右对照；可编辑 `PUT /api/v1/segments/{id}`。
6. 桌面「导出 TXT」→ `GET /api/v1/chapters/{id}/export?format=txt`。

## 运行

依赖与命令见 `plan.md`「验证」与仓库根 `README.md`。要点：`docker compose up -d postgres redis minio` → backend `uv run alembic upgrade head` + `uvicorn` + `arq` → desktop `pnpm install && pnpm --filter desktop tauri dev`。翻译需配置可用模型端点（`.env` 的 OpenAI 兼容 base_url/key/model，或本地 Ollama）。
