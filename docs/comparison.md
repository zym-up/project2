# project1 vs project2: Architecture Comparison

## 1. Overview

Both projects implement the same functionality — a Data Scientist Agent (AI-powered data analysis tool for automotive R&D engineers) — but differ fundamentally in their LLM orchestration architecture.

| Dimension | project1 | project2 |
|-----------|----------|----------|
| LLM calls | Raw OpenAI SDK | LangChain `ChatOpenAI` |
| Agent reasoning | Custom `AnalysisAgent` class | LangChain `AgentExecutor` + `create_tool_calling_agent` |
| Step orchestration | `step_executor.py` (if-else dispatch) | LangGraph `StateGraph` |
| Tool management | None (frontend sends `method` name) | LangChain `StructuredTool` (12 tools) |
| Knowledge retrieval | TF-IDF keyword matching | Chroma RAG semantic vector search |
| State management | Manual JSON read/write (`state.json`) | LangGraph State + `SqliteSaver` Checkpointer |
| Streaming | Custom SSE generator | LangGraph `astream_events` |

## 2. Architecture Diagrams

### project1

```
User -> Vue Frontend -> manual step clicking -> FastAPI -> step_executor(if-else) -> engine functions
                           |                        |
                           +-- human picks method --+-- llm_agent (raw OpenAI API)
```

### project2

```
User -> Vue Frontend -> natural language -> FastAPI SSE -> LangGraph StateGraph
                                                              |-- understand_intent (RAG)
                                                              |-- plan_analysis (LLM + Tools)
                                                              |-- execute_step (Tool Calling)
                                                              |-- interpret_result (LLM)
                                                              |-- decide_next (deterministic)
                                                              +-- generate_conclusion (LLM)
```

## 3. Core Differences (Layer by Layer)

### 3.1 LLM Orchestration

**project1** (`llm_agent.py`): ~300 lines of custom code using the `openai` library directly.
- `AnalysisAgent` class with manual prompt construction
- Manual JSON parsing from LLM responses
- Custom `chat_stream` iterator for SSE

**project2** (`agent/analysis_agent.py`): ~35 lines using LangChain.
```python
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, ...)
```
- Framework handles prompt templating, tool binding, and streaming
- Add a feature = add a Tool. Agent discovers it automatically.

### 3.2 Step Orchestration

**project1** (`step_executor.py`): Large if-else dispatch:
```python
def execute_step(step_type, params, df):
    if step_type == "clean": return _clean(df, params)
    elif step_type == "eda": return _eda(df, params)
    elif step_type == "feature": return _feature(df, params)
    elif step_type == "model": return _model(df, params)
```

**project2** (`graph/workflow.py`): StateGraph with conditional routing:
```python
workflow.add_conditional_edges("interpret_result", decide_next, {
    "execute": "execute_step",
    "generate_conclusion": "generate_conclusion",
})
```
- New analysis types don't need `step_executor` changes
- Conditions are deterministic code, not LLM guesses
- Natural support for loops and branching

### 3.3 Tool Calling

**project1**: Frontend must know exact method names:
```json
{"step_type": "eda", "method": "correlation", "params": {"columns": ["a", "b"]}}
```
Adding an operation requires: engine function + step_executor branch + LLM prompt update + frontend form.

**project2**: User speaks naturally, LLM picks the tool:
```
User: "What factors correlate with seat satisfaction?"
-> LLM auto-calls: correlation_analysis(columns=["seat_satisfaction"])
-> Then auto-calls: feature_importance(target="seat_satisfaction")
```
Adding an operation = one `StructuredTool` definition. Frontend stays unchanged.

### 3.4 Knowledge Retrieval

| Aspect | project1 (TF-IDF) | project2 (Chroma RAG) |
|--------|-------------------|----------------------|
| Method | Keyword frequency | Semantic vector similarity |
| Synonyms | "seat" won't match "cushion" | Semantic understanding covers synonyms |
| Documents | Whole file, no chunking | Chunked storage, precise retrieval |
| Storage | YAML + TXT files | Chroma vector DB (persistent) |
| Interface | Custom `KnowledgeBase.search()` | LangChain `BaseRetriever.invoke()` |
| Code size | ~150 lines | ~30 lines core logic |

### 3.5 State Management

**project1**: Manual JSON serialization:
```python
pm.save_state(project_id, {"rounds": [...], "current_round": 0})
pm.save_chat_history(project_id, [...])
```

**project2**: Graph State + Checkpointer:
```python
workflow.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))
# State auto-persisted. Browser close -> reopen -> resume from checkpoint.
```

### 3.6 Streaming Output

**project1**: Custom SSE generator (30+ lines per endpoint).

**project2**: One-line LangGraph abstraction:
```python
async for event in workflow.astream_events(initial_state, version="v2"):
    yield f"data: {json.dumps(event)}\n\n"
```

## 4. Line Count Comparison

| Module | project1 | project2 | Delta |
|--------|----------|----------|-------|
| `engine/` (except llm_agent + step_executor) | ~2500 | ~2500 | Same |
| `engine/llm_agent.py` | ~300 | Deleted | -300 |
| `engine/step_executor.py` | ~200 | Deleted | -200 |
| `graph/` | 0 | ~430 | +430 |
| `agent/` | 0 | ~120 | +120 |
| `agent/rag/` | 0 | ~140 | +140 |
| `backend/` | ~400 | ~350 | -50 |
| `frontend/` (API + Store) | ~300 | ~240 | -60 |
| **Total** | **~3900** | **~3780** | **~120 fewer** |

While total lines are similar, project2's code is distributed across smaller, more focused files. Framework-provided capabilities (retry, state recovery, tracing) don't count as lines but exist in project2 and not in project1.

## 5. Developer Experience

### 5.1 Adding a New Analysis Operation

**project1** (5 steps):
1. Implement function in `engine/`
2. Add `if` branch in `step_executor._<type>()`
3. Add description in `llm_agent.build_system_prompt()`
4. Add form control in Vue frontend
5. Test end-to-end flow

**project2** (2 steps):
1. Add `StructuredTool` in `graph/tools.py`
2. Run tests

### 5.2 Debugging

**project1**: `print`/`logging` debugging. Manually trace state changes across files.

**project2**: Set `LANGCHAIN_TRACING_V2=true` for LangSmith visual tracing. Every LLM call, tool call, and state mutation is visualized on a timeline with inputs/outputs.

### 5.3 Testing

**project1**: Need to mock frontend request parameter structures.

**project2**: Test tools and graph nodes directly. `MemorySaver` makes workflow state testing trivial:
```python
app = workflow.compile(checkpointer=MemorySaver())
result = app.invoke(initial_state, config)
assert result["next_action"] == "replan"
```

## 6. Learning Curve

| Aspect | project1 | project2 |
|--------|----------|----------|
| Initial ramp-up | Low (pure Python) | Medium (Agent/Graph/Tool concepts) |
| Concept count | Few | More (StateGraph, Tool, AgentExecutor, RAG) |
| Documentation | None (custom code) | Rich LangChain/LangGraph docs |
| Best for | Small, simple agents | Complex multi-step agents needing state |

## 7. When to Choose Which

**Choose project1 (hand-rolled) when:**
- Team is unfamiliar with LangChain ecosystem
- Agent logic is simple (3-5 linear steps)
- You need absolute control over every detail
- Minimizing dependencies is a primary concern

**Choose project2 (LangChain/LangGraph) when:**
- Agent has complex control flow (conditions, loops, human-in-the-loop)
- You need state persistence and resume-after-crash
- Semantic search / RAG capability is needed
- You want the framework community to keep providing new capabilities
- Team is willing to invest time learning the framework

## 8. Academic Foundations

project2's architecture is grounded in established research:

- **ReAct** (Yao et al., 2022): Reasoning + Acting loop
- **Plan-and-Solve** (Wang et al., 2023): Plan first, then execute — 30%+ lower error rate
- **Tool-Augmented LLM** (Schick et al., 2023 / Toolformer): Extend LLM capability via tool interfaces
- **State Machine Agent** (LangGraph, 2024): Constrain agent behavior with explicit state graphs
- **RAG** (Lewis et al., 2020): Retrieve relevant knowledge before generation

See `docs/superpowers/specs/2026-07-19-project2-langgraph-design.md` (in project1) for the full theoretical discussion.
