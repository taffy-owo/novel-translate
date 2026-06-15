# novel-translate 项目创建计划

## Context（为什么做这个）

上一轮对话里你让我读 `D:\download\deep-research-report.md`（《超长篇小说翻译系统产品设计与技术方案研究报告》）并「帮我创建项目」，问到项目命名时被打断。现已确认：

- 项目名 **`novel-translate`**，目录 `D:\Project\novel-translate`（尚未创建）。
- 形态选 **完整混合架构**：Tauri 桌面 + FastAPI + Redis worker + Postgres/pgvector + 对象存储（完全按报告主推方案）。
- 首期交付范围由我决定 → **完整 monorepo 骨架 + 一条端到端 walking skeleton**。
- 不参照本地任何 sibling 项目（vaultone/爱素书屋 等），纯按报告新建。
- **具体开发交给本机 Codex CLI（v0.139.0，已认证 api_key），我负责编排、审核、引导**；自主度选「全自动、事后审」。

目标产出：一个结构完整、`docker compose` 可起、且能真实跑通「导入→分段→翻译→对照→导出」一条链路的工程底座；其余高级能力按报告里程碑留接口 + TODO。

**语言对默认 日(ja)→中(zh-CN)**（报告示例是 en→zh，按你做日轻小说的实际史改默认；架构本身语言无关）。

## 锁定的架构决策（来自报告）

| 维度 | 采用 |
|---|---|
| 产品形态 | Tauri 2 桌面客户端 + FastAPI 云端编排 + Redis worker（混合） |
| 模型接入 | 双通道适配：OpenAI-compatible（首发主力，接 OpenAI/vLLM/Ollama/llama.cpp）+ Anthropic 原生（最小实现） |
| 长文本策略 | 分段翻译 + 术语表 + 分层记忆 + 全局校正（首期只实现「分段翻译」，其余留接口） |
| 存储 | PostgreSQL + pgvector（向量与业务同库）；MinIO 作 S3 兼容对象存储 |
| 队列 | Redis + arq（async 原生，贴合 FastAPI） |
| 协作 | 单用户优先；status/version 字段预留，软锁/审校后置 |
| 导出 | 章节导出优先（首期 TXT），整书构建后置 |

## 执行模型：Codex CLI 编排（我审核引导，不亲手写业务代码）

我不直接写业务代码；按下面的循环驱动 Codex，逐个任务派发→审核→纠偏：

```
codex exec --dangerously-bypass-approvals-and-sandbox \
  -C D:\Project\novel-translate \
  "<本任务的精确指令：目标文件、接口约定、约束、完成判据>"
```

- **预置（任务 0，我亲手做的唯一落盘动作）**：`git init` 该目录（Codex 默认要 git 仓库，且我要靠 `git diff` 审核 + 可用 `codex apply`）；写入 `AGENTS.md`（父级设计规则 + 本计划要点 + 「日→中、provider 接口稳定」约束），让每次 `codex exec` 自动加载为上下文；把 `docs/deep-research-report.md` 拷进去作 Codex 可读规格。
- **每个任务**：给 Codex 一段自包含 prompt（引用 `AGENTS.md`/`docs` 里的对应小节 + 明确文件路径 + 完成判据，如「`pytest tests/test_ingest.py` 全绿」）。全自动模式下 Codex 自行写码、`uv sync`/`pnpm install`、起 docker、跑迁移与测试。
- **审核门（我来）**：任务结束后 `git --no-pager diff`/`git status` 看改动，复核 Codex 自报的测试结果，必要时自己跑一遍关键命令核验；对照本计划与 `AGENTS.md` 设计规则查问题（命名消歧、边界处校验、不用 flag 切行为、provider 抽象是否被绕开）。
- **纠偏**：发现问题用 `codex exec resume --last "<修正指令>"` 续同一会话，或新派一段带审查意见的 prompt；通过后 `git commit` 固化，再进入下一任务。
- **里程碑级复查**：骨架与 walking skeleton 跑通后，用 `codex exec review`（或本会话 /code-review）对全量 diff 做一次正确性 + 简化复审。



```
novel-translate/
├─ README.md  AGENTS.md  .gitignore  .env.example
├─ docker-compose.yml              # postgres(pgvector) / redis / minio / api / worker
├─ pnpm-workspace.yaml  package.json  turbo.json
├─ apps/desktop/                   # Tauri2 + React19 + Vite + TS + Tailwind
│  ├─ index.html  vite.config.ts  tsconfig.json  tailwind.config.js  package.json
│  ├─ src/  (main.tsx, App.tsx, api/, components/, pages/, stores/, lib/)
│  └─ src-tauri/  (Cargo.toml, tauri.conf.json, build.rs, capabilities/, src/lib.rs+main.rs)
├─ packages/
│  ├─ api-client/                  # 调后端的 TS 客户端 + 共享类型
│  └─ tsconfig/                    # 共享 tsconfig base
├─ backend/                        # 单 Python 包，双入口(api / worker)，共享 models/adapters
│  ├─ pyproject.toml  alembic.ini
│  ├─ src/novel_translate/
│  │  ├─ api/      (main.py, deps.py, v1/{projects,chapters,segments,translations,glossary,exports}.py)
│  │  ├─ worker/   (main.py=WorkerSettings, tasks/translate_segment.py)
│  │  ├─ core/     (config.py, db.py, redis.py, storage.py, logging.py)
│  │  ├─ modules/
│  │  │  ├─ projects/   (models.py, schemas.py, service.py)
│  │  │  ├─ ingest/     (txt.py, segment.py, chapters.py, epub.py*, docx.py*)
│  │  │  ├─ glossary/   (models.py, schemas.py, service.py*)
│  │  │  ├─ memory/     (models.py, snapshot.py*, retrieval.py*)   # pgvector
│  │  │  ├─ translation/(request.py, schemas.py, pipeline.py*)
│  │  │  ├─ providers/  (base.py, openai_compatible.py, anthropic.py, registry.py)
│  │  │  └─ exports/    (chapter.py, project_zip.py*)
│  │  └─ db/      (base.py, migrations/)
│  └─ tests/
├─ infra/postgres/init.sql         # CREATE EXTENSION IF NOT EXISTS vector;
└─ docs/  (architecture.md, phase-map.md, deep-research-report.md[拷贝])
```
`*` = 本期留 stub + TODO（仅签名/接口，不实现完整逻辑）。

## Walking skeleton（本期真实打通的唯一纵切）

数据模型（SQLAlchemy 2.0，`Mapped[]`，async）——**完整实现**：
- `Project(id, name, source_lang='ja', target_lang='zh-CN', provider_config: JSONB, created_at)`
- `Chapter(id, project_id→, title, order_index, source_format, created_at)`
- `Segment(id, chapter_id→, order_index, source_text, target_text|None, status: enum[pending|translating|done|error], error|None, updated_at)`

**建表 + 迁移但仅最小逻辑**（打通 pgvector，逻辑留 TODO）：
- `GlossaryTerm(id, project_id→, source, target, aliases: JSONB, scope: enum, status: enum[draft|approved|deprecated], constraint_kind: enum[hard|soft], notes)` —— 字段按报告术语表 JSON
- `MemorySnapshot(id, project_id→, level: enum[book|volume|chapter], version, content: JSONB, embedding: Vector(1536), created_at)`

端到端流程（每层都真实经过）：
1. 桌面「新建项目」→ `POST /api/v1/projects`
2. 桌面用 Tauri `dialog.open` 选 `.txt` → 读文件 → `POST /api/v1/projects/{id}/chapters:import-txt {title, content}`；`ingest.txt`+`ingest.segment` 按段落/空行切成 `Segment(status=pending)`
3. 桌面「翻译本章」→ `POST /api/v1/chapters/{id}:translate` → 后端把 pending segments 入队 arq
4. `worker/tasks/translate_segment.py`：取 segment → `translation.request` 构 `TranslateSegmentRequest`（带 local_context 前后句）→ `providers.openai_compatible` 调模型(temperature 0.2) → 写回 `target_text`/`status`
5. 桌面轮询 `GET /api/v1/chapters/{id}`（react-query）→ 原文/译文左右对照；可编辑译文 `PUT /api/v1/segments/{id}`
6. 桌面「导出」→ `GET /api/v1/chapters/{id}:export?format=txt` → `exports.chapter` 拼译文返回

Provider 首发：`openai_compatible`（`base_url`/`api_key`/`model` 可配，兼容 OpenAI/vLLM/Ollama/llama.cpp）。同时落 `anthropic.py` 最小同步实现。
> 实现 `anthropic.py` 前先用 **claude-api skill** 核对当前 Anthropic 模型 ID（默认 `claude-sonnet-4-6`）、SDK 用法与价格，避免写死过期 ID。`base.py` 定义 `ProviderAdapter.translate(req) -> TranslateSegmentResult` 抽象，`registry.py` 按 `provider_config.kind` 选适配器（不用 if/flag 堆叠，按报告「接口稳定、模型可替换」）。

## 留 stub 的能力 → 报告里程碑映射（见 docs/phase-map.md）

| 能力 | 落点（stub） | 报告阶段 |
|---|---|---|
| 分层记忆/快照检索、全局一致性校正 | `memory/`, `translation/pipeline.py` | d2,d3 |
| 术语自动抽取 + 审批流 | `glossary/service.py` `extract()/approve()` | d1 |
| DOCX/EPUB 导入、整书构建 | `ingest/{epub,docx}.py`, `exports/project_zip.py` | b2,e4 |
| 审校/软锁/版本历史 | 模型 status/version 字段预留 | e1,e2 |
| RLS/RBAC、审计、OpenTelemetry、桌面签名打包 | `core/config.py` 钩子 + docs | f1,f3 |
| Batch API / Prompt Caching | `providers/*` TODO | 成本章节 |

## 技术栈与版本

- 前端：Tauri 2、React 19、Vite、TypeScript 5、Tailwind、`zustand`（状态）、`@tanstack/react-query`（请求轮询）、`react-router`；pnpm workspace。
- 后端：Python 3.11、`uv`、FastAPI、uvicorn、SQLAlchemy 2.0(async)、asyncpg、Alembic、pydantic v2 + pydantic-settings、redis + `arq`、`pgvector`、`openai` SDK、`anthropic` SDK、MinIO/`boto3`。
- 基础设施（docker-compose）：`pgvector/pgvector:pg17`、`redis:7`、`minio`；外加 `api`、`worker` 两个服务跑同一后端镜像。

## Codex 任务队列（我逐个派发 → 审核 → 纠偏 → commit）

- **T0 预置（我亲手）**：`git init`；写 `AGENTS.md`、`README` 占位；拷报告进 `docs/`。
- **T1 骨架+根配置**：pnpm-workspace、package.json、.gitignore、.env.example、docker-compose.yml、infra/postgres/init.sql、docs/。判据：`docker compose config` 通过。
- **T2 后端地基**：pyproject + `core`(config/db/redis) + `db.base` + 三核心模型 + Alembic 初始迁移 + FastAPI `/health`。判据：`alembic upgrade head` 成功、`/health` 200。
- **T3 翻译主链路**：`projects`(CRUD) + `ingest`(txt+segment) + `providers`(base+openai_compatible+anthropic) + `translation.request` + `exports.chapter`(txt)。判据：相应 pytest 全绿。
- **T4 worker 入队**：arq `WorkerSettings` + `translate_segment`；api `:translate` 入队。判据：mock provider 下一段 TXT 从 pending→done。
- **T5 知识层落表**：`glossary` + `memory` 模型(含 `Vector` 列)与迁移、stub service。判据：pgvector 建表成功、`embedding` 列可写读。
- **T6 桌面端**：Tauri2 + `src-tauri` 选文件命令 + React 页面(项目/导入/对照编辑/导出) + `packages/api-client` + react-query 轮询。判据：`pnpm --filter desktop tauri dev` 起得来、链路可手动跑通。
- **T7 文档+复查**：docs/architecture.md + phase-map.md；`codex exec review` 全量复审 + 我冒烟验证。

> 实现 `providers/anthropic.py` 前，我先用 **claude-api skill** 核对当前 Anthropic 模型 ID（默认 `claude-sonnet-4-6`）/SDK/价格，把准确信息写进给 Codex 的 prompt，避免它用过期 ID。

## 验证（端到端）

> 全自动模式下这些命令由 Codex 自行执行；我在审核门复核它的输出，并亲手重跑下列关键命令核验，不只看它自报。

```
# 1. 起依赖
docker compose up -d postgres redis minio
# 2. 后端
cd backend && uv sync && uv run alembic upgrade head
uv run uvicorn novel_translate.api.main:app --reload         # 终端 A
uv run arq novel_translate.worker.main.WorkerSettings        # 终端 B
# 3. 配 .env：OPENAI 兼容 base_url/key/model（无 GPU 可指 Ollama 本地端点）
```
- curl 串一遍：create project → import-txt（贴一段日文）→ :translate → 轮询 GET chapter 看到中文译文 → :export?format=txt。
- pytest：projects CRUD、txt 分段、openai_compatible 适配器（用 mock/`respx`）、chapter 导出。
- 前端：`pnpm install && pnpm --filter desktop tauri dev`，手动跑同一链路并截图确认对照视图与导出。

## 假设（如不同请在批准时指出）

- 默认语言对 日→中；provider 首发用 OpenAI-compatible 单适配器 + Anthropic 最小实现。
- 队列用 arq（报告写「Redis 队列」，arq 满足且 async 原生）。
- 对象存储(MinIO)在骨架内起好，但本期导出走 API 直接返回，不强制入对象存储（接口预留）。
- 沿用父目录 `D:\Project\AGENTS.md` 设计规则，并在项目内 `AGENTS.md` 重申，供 Codex 每次 `codex exec` 自动加载。
- 开发交给 Codex CLI 全自动执行（`--dangerously-bypass-approvals-and-sandbox`），我逐任务事后审 `git diff`+复核测试并纠偏；`novel-translate` 设为独立 git 仓库（父 `D:\Project` 非仓库）。
