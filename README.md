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

见 `docs/plan.md`「验证」一节（docker compose 起依赖 → uv 起后端与 worker → pnpm 起桌面端）。
