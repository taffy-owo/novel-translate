# novel-translate

超长篇小说翻译系统 —— 桌面优先的混合架构（Tauri 桌面 + FastAPI 编排 + Redis/arq worker + PostgreSQL/pgvector + MinIO）。

支持任意第三方模型 API 或本地模型、可配置提示词、自动术语表与上下文记忆、批量导入本地文件、原译文对照精修、章节导出（整书构建后置）。默认语言对 日→中，架构语言无关。

> 设计与技术规格见 [`docs/deep-research-report.md`](docs/deep-research-report.md)；当前实施计划见 [`docs/plan.md`](docs/plan.md)；Agent 工作约定见 [`AGENTS.md`](AGENTS.md)。

## 现状

搭建中：完整 monorepo 骨架 + 一条端到端 walking skeleton（导入 TXT → 分段 → 翻译 → 对照 → 导出）。其余能力按报告里程碑分阶段补齐。

## 结构

```
apps/desktop/      Tauri 2 + React 19 桌面客户端
backend/           FastAPI 编排 + arq worker（单 Python 包，双入口）
packages/          共享 TS（api-client / tsconfig）
infra/             docker 初始化脚本
docs/              规格与计划
```

## 快速开始

**Windows 一键启动**：先打开 Docker Desktop，然后双击仓库根目录的 `start.bat` —— 它会依次拉起 postgres/redis/minio、应用数据库迁移、在独立窗口启动后端 API 与 worker，并打开桌面端（首次会编译 Rust，窗口需等 1–2 分钟）。停止用 `stop.bat`。

翻译模型在 `backend/.env` 配置（`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL`，OpenAI 兼容接口）；每分钟请求上限由 `PROVIDER_RPM`（默认 20）限流。worker 经本地代理访问网关的设置见 `start.bat`。

手动启动步骤（或非 Windows）见 `docs/plan.md`「验证」一节。
