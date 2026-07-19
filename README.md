# DS Agent v2 — LangChain + LangGraph

基于 LangChain/LangGraph 的数据科学家 Agent，面向汽车研发工程师的数据分析工具。

## 与 v1 的区别

v1 (project1) 的 LLM 编排层是手写的，v2 用 LangChain AgentExecutor + LangGraph StateGraph 替换，engine 算法层保持不变。详见 [docs/comparison.md](docs/comparison.md)。

## 快速开始

1. 安装 Python 依赖: `pip install -r requirements.txt`
2. 配置 `config.json` 中的 LLM API
3. 初始化知识库: `python scripts/init_rag.py`
4. 启动后端: `uvicorn backend.main:app --reload --port 8502`
5. 启动前端: `cd frontend && npm run dev`

## 技术栈

- **编排**: LangGraph StateGraph
- **Agent**: LangChain AgentExecutor + Tool Calling
- **知识检索**: Chroma RAG (语义向量搜索)
- **后端**: FastAPI + SSE 流式
- **前端**: Vue 3 + Element Plus
- **分析**: pandas, scikit-learn, xgboost, plotly
