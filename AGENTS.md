# novel-translate — Agent 工作约定

> 本文件由编排者（Claude）维护，Codex 每次 `codex exec` 自动加载。**动手前先读 `docs/plan.md`（完整计划）与 `docs/deep-research-report.md`（技术规格）。**

## 这是什么

超长篇小说翻译系统。**桌面优先的混合架构**：Tauri 桌面客户端负责本地文件与精修，FastAPI 云端负责编排，Redis(arq) worker 跑翻译，PostgreSQL+pgvector 存业务与向量，MinIO 作对象存储。

**当前阶段**：搭「完整 monorepo 骨架 + 一条端到端 walking skeleton」。walking skeleton = 新建项目 → 导入 TXT → 分段 → 调模型翻译 → 原译对照 → 导出 TXT，真实打通每一层。其余能力按 `docs/plan.md` 的里程碑映射**只留接口 + TODO，不实现**。不要超范围把后续阶段的功能提前写了。

## 技术栈（用这些，别换）

- 前端：Tauri 2、React 19、Vite、TypeScript 5、Tailwind、`zustand`、`@tanstack/react-query`、`react-router`；pnpm workspace。
- 后端：Python 3.11、**uv** 管依赖、FastAPI、uvicorn、**SQLAlchemy 2.0 async**（`DeclarativeBase` + `Mapped[]` + `mapped_column`）、asyncpg、Alembic、pydantic v2 + pydantic-settings、redis + **arq**、`pgvector`、`openai` SDK、`anthropic` SDK、MinIO/`boto3`。
- 基础设施：docker-compose 起 `pgvector/pgvector:pg17`、`redis:7`、`minio`、`api`、`worker`。

## 仓库布局（backend 为单包双入口：api 与 worker 共享 models/adapters）

见 `docs/plan.md`「仓库布局」一节，按那个结构落文件。后端代码在 `backend/src/novel_translate/{api,worker,core,modules,db}`。模块：`projects / ingest / glossary / memory / translation / providers / exports`。

## 设计规则（强制，违反就重写）

1. **命名消歧**。禁用 `data/info/result/handler/manager/process/utils/helper/do_*/*_impl` 这类默认名，用描述具体事物/动作的名字。
2. **边界处校验一次，内部信任不变量**。不要在内部可信边界散落防御式判断；同一检查出现 3+ 次就重构边界。
3. **注释写契约/不变量/理由/约束/被否方案**，不要复述代码或给烂命名/烂边界擦屁股。
4. **不要用 mode/flag 参数切特殊行为**（不用 bool/enum/字符串模式/options 包切分支）。差异是真实的就拆成各自抽象拥有的独立操作。
5. **正确的归属、完整的操作**。复杂度放在决策/不变量/外部依赖所在处；暴露完整操作而非让调用方拼步骤。

## 本项目硬约束

- **默认语言对 日(ja)→中(zh-CN)**；但所有代码必须语言无关，语言对来自 `Project.source_lang/target_lang`，不要写死「日」「中」到逻辑里。
- **Provider 抽象不可绕过**：`providers/base.py` 定义 `ProviderAdapter.translate(req) -> TranslateSegmentResult` 抽象；`registry.py` 按 `provider_config.kind` 选适配器。新增 provider = 加一个 adapter，**不是**在调用处加 `if kind == ...`。首发实现 `openai_compatible`（可配 base_url/api_key/model，兼容 OpenAI/vLLM/Ollama/llama.cpp）与 `anthropic` 最小实现。
- **翻译任务用统一 schema**：`translation/request.py` 的 `TranslateSegmentRequest` 带 `source_text`、前后句 `local_context`、`glossary_terms`、`style_guide`、`memory_hits`（参见报告示例 JSON）；响应结构化（translation + new_term_candidates + consistency_warnings + summary_delta），即使首期后两者为空。
- **数据模型**：`Project/Chapter/Segment` 完整实现；`GlossaryTerm/MemorySnapshot`（`embedding: Vector(1536)`）建表 + 迁移但 service 留 stub。status/version 字段预留给后续审校。
- 错误处理在 API 边界统一，segment 翻译失败写 `status='error'` + `error` 文本，不让 worker 整个崩。

## 怎么算完成

- Python：`uv run ruff check` 无错；对应 `pytest` 全绿；`uv run alembic upgrade head` 能跑。
- 每个任务有明确判据（见 `docs/plan.md` 的 T1–T7），达成判据才算完成。
- 提交信息用中文祈使句，简述改动；一个任务一组提交。
