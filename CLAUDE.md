# CLAUDE.md

## Project Overview

数据科学家 Agent v2 — 基于 LangChain + LangGraph 的汽车研发数据分析工具。

架构分层：
- engine/: 数据分析算法（复制自 project1，纯函数）
- graph/: LangGraph StateGraph 工作流（状态管理 + 节点编排）
- agent/: LangChain Agent + RAG 知识检索
- backend/: FastAPI 后端
- frontend/: Vue 3 前端

## Development Commands

- Install Python deps: `pip install -r requirements.txt`
- Start backend: `uvicorn backend.main:app --reload --port 8502`
- Start frontend: `cd frontend && npm run dev`
- Run tests: `pytest tests/ -v`
- Init RAG: `python scripts/init_rag.py`

## Architecture

project1 vs project2 核心差异：
- llm_agent.py + step_executor.py → graph/ (StateGraph) + agent/ (AgentExecutor)
- TF-IDF 知识检索 → Chroma RAG 语义检索
- 手动 JSON 状态管理 → Graph State + SqliteSaver Checkpointer

## Language Preference
Please always communicate with me in Simplified Chinese.
