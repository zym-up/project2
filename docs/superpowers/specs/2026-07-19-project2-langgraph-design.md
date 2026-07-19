# project2: LangChain + LangGraph 复现设计方案

> 基于 project1 的数据科学家 Agent，用 LangChain/LangGraph 重新实现 LLM 编排层，保留 engine 算法层。

## 一、动机与目标

project1 的 LLM 编排层是手写的（`llm_agent.py` + `step_executor.py`），存在以下问题：

1. **调度逻辑耦合**：`step_executor.py` 用大型 if-else 分派分析操作，每加一个方法要改两处
2. **状态管理脆弱**：分析状态靠手动 JSON 序列化，多轮对话中上下文拼接容易出错
3. **扩展困难**：想加"结果异常自动重试"、"人工确认断点"等功能，需要改动大量流程代码
4. **无标准化工具接口**：LLM 不知道有哪些操作可用，前端必须传递精确的 `method` 名

project2 用 LangChain + LangGraph 解决这些问题，同时保持 engine 算法层不变。

## 二、学术命名与理论依据

### 架构命名

**Plan-and-Execute Agent with Tool-Augmented Reasoning and RAG**（计划-执行式工具增强推理代理，带检索增强生成）。

### 理论来源

**1. ReAct 模式 (Yao et al., 2022)** — *Reasoning + Acting*

核心思想：LLM 不在黑盒中直接输出答案，而是在"思考→行动→观察→思考→..."的循环中解决问题。project2 的 `plan_analysis → execute_step → interpret_result → decide_next` 就是这个循环的工程化实现。

**2. Plan-and-Solve (Wang et al., 2023)**

核心发现：让 LLM 先制定完整计划再逐步执行，比边想边做的错误率低 30%+。直接支撑了先 `plan_analysis` 生成完整步骤列表，再进入执行循环的设计。

**3. Tool-Augmented LLM (Schick et al., 2023 / Toolformer)**

LLM 本身不能操作数据，通过 Tool 接口（函数调用）扩展能力边界。project2 把每个分析操作封装为 LangChain Tool，LLM 通过 Function Calling 自主选择调用哪个。

**4. State Machine Agent (LangGraph 设计哲学, 2024)**

核心洞察：纯 Agent 循环（ReAct）在复杂任务中容易"跑偏"或死循环。用显式状态图（StateGraph）约束 Agent 行为，把 Agent 从"黑盒对话"变成"可控的状态机"。

**5. RAG (Lewis et al., 2020)**

检索增强生成：在 LLM 推理前从外部知识库检索相关信息注入 prompt，提升生成质量和领域适配性。

### 分层依据

对应 Andrew Ng 2024 年提出的 Agentic Design 原则——不要用 LLM 做代码擅长的事：

```
┌──────────────────────────────────────────┐
│  Agent 层  │  决策（What to do）          │  LLM 擅长的事
├──────────────────────────────────────────┤
│  Graph 层  │  编排（When & How）          │  状态机擅长的事
├──────────────────────────────────────────┤
│  Tools 层  │  调度（Which function）      │  Tool Calling 擅长的事
├──────────────────────────────────────────┤
│  Engine 层 │  算法（Math & Logic）        │  已有稳定实现，不改
└──────────────────────────────────────────┘
```

project1 的问题恰恰是混淆了这些层——决策、编排、调度全挤在 `llm_agent.py` 和 `step_executor.py` 里。

## 三、整体架构

```
project2/
├── engine/                    # 从 project1 复制，独立维护（11 个模块不变）
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── eda.py
│   ├── feature_engineer.py
│   ├── modeler.py
│   ├── reporter.py
│   ├── sandbox.py
│   ├── config.py
│   ├── project_manager.py
│   ├── knowledge.py           # 改为 LangChain BaseRetriever 接口
│   └── __init__.py
│
├── graph/                     # 新增：LangGraph 工作流层
│   ├── state.py               # AnalysisState TypedDict
│   ├── nodes.py               # 各节点实现
│   ├── workflow.py            # StateGraph 构建与编译
│   └── tools.py               # LangChain Tool 封装（调 engine）
│
├── agent/                     # 新增：LangChain Agent + RAG
│   ├── analysis_agent.py      # AgentExecutor
│   ├── prompts.py             # System prompt 模板
│   └── rag/
│       ├── loader.py          # 文档加载
│       ├── splitter.py        # 文档分块
│       ├── embeddings.py      # 向量化（默认 DeepSeek API，可配置）
│       ├── store.py           # Chroma 向量库
│       └── retriever.py       # LangChain Retriever
│
├── backend/                   # 基于 project1 改造
│   ├── main.py                # FastAPI 入口
│   ├── deps.py                # 共享依赖
│   ├── routers/
│   │   ├── config.py          # 复用
│   │   ├── projects.py        # 复用
│   │   ├── analysis.py        # 改造：调用 Graph workflow + SSE 流
│   │   └── reports.py         # 微调适配
│   └── models/schemas.py      # 微调
│
├── frontend/                  # 基于 project1 改造
│   └── src/
│       ├── api/index.js       # SSE 适配 astream_events 事件格式
│       ├── stores/project.js  # state 结构适配
│       └── views/
│           ├── Analysis.vue   # 展示 Graph 实时执行过程
│           ├── NewProject.vue # 复用
│           ├── Settings.vue   # 复用
│           └── ReportPreview.vue  # 复用
│
├── knowledge/                 # 复用
├── tests/                     # 新增 LangGraph/RAG 测试
└── docs/
    └── comparison.md          # project1 vs project2 全面对比
```

### 删除的模块

| 文件 | 原因 | 替代 |
|------|------|------|
| `engine/llm_agent.py` | 手写 Agent 逻辑 | `agent/analysis_agent.py` (LangChain AgentExecutor) |
| `engine/step_executor.py` | 手写 if-else 调度 | `graph/tools.py` (LangChain Tool Calling) |

### 不改动的模块

`engine/` 其余 11 个模块的核心逻辑不动——它们是纯函数（拿参数 → 返回结果），不关心谁在调用它们。Tool 层只是包一层薄壳。

## 四、LangGraph StateGraph 工作流

### AnalysisState 定义

```python
class AnalysisState(TypedDict):
    # 输入
    user_input: str
    df_info: dict
    df: pd.DataFrame

    # RAG 上下文
    rag_context: str

    # 计划
    plan: list[AnalysisStep]
    current_step_index: int

    # 执行结果（跨步骤累积）
    results: list[StepResult]
    context_summary: str

    # 控制流
    next_action: str    # "execute" | "skip" | "replan" | "done"
    error_message: str
```

### 节点和边

```
understand_intent ──→ plan_analysis ──→ execute_step ──→ interpret_result
                                     ↑                      │
                                     │    ┌─────────────────┘
                                     │    ▼
                                     └── decide_next ──→ generate_conclusion
                                       (条件路由)
```

- **understand_intent**：RAG 检索 + 意图解析，注入领域知识
- **plan_analysis**：LLM + Tool Calling 生成分析步骤列表
- **execute_step**：执行当前步骤的 Tool 调用
- **interpret_result**：LLM 解读执行结果（不需要 Tool）
- **decide_next**：确定性代码逻辑判断——继续/跳过/重新规划/完成

### 关键设计决策

**为什么 Tool Calling 不够，还需要 StateGraph？**

Tool Calling 解决"选哪个函数"，StateGraph 解决"调用之后怎么办"：

1. **状态自动累积**：Tool Calling 每次调用独立。Graph 的 state 在节点间自动传递，`interpret_result` 产出的解读自动注入到 `decide_next` 的决策
2. **确定性控制流**：R² < 0.3 → 自动回到 `plan` 重新规划，这是代码逻辑不是 LLM 判断，不会出错
3. **人工断点**：`execute_step` 前可插入 `interrupt`，前端确认后再继续

### 流式输出

利用 LangGraph 的 `astream_events`：

```python
async for event in workflow.astream_events(initial_state, version="v2"):
    yield f"data: {json.dumps(event)}\n\n"
```

前端收到的事件类型：`on_chat_model_stream`（逐 token）、`on_tool_start`/`on_tool_end`（工具调用进度）、`on_chain_end`（节点完成）。

## 五、Tool 设计

每个分析操作封装为一个 LangChain StructuredTool，LLM 通过 Function Calling 自主决定调用：

```python
tools = [
    # 数据清洗
    StructuredTool(name="clean_data", description="去重、填充缺失值、检测异常值",
                   args_schema=CleanInput, func=run_clean),
    # EDA
    StructuredTool(name="describe_numeric", description="数值列描述统计",
                   args_schema=DescribeNumericInput, func=run_describe_numeric),
    StructuredTool(name="correlation_analysis", description="相关性矩阵+热力图",
                   args_schema=CorrelationInput, func=run_correlation),
    StructuredTool(name="distribution_plot", description="单变量分布图",
                   args_schema=DistributionInput, func=run_distribution),
    # 特征工程
    StructuredTool(name="scale_features", ...),
    StructuredTool(name="encode_categorical", ...),
    # 建模
    StructuredTool(name="train_regression", ...),
    StructuredTool(name="evaluate_model", ...),
    StructuredTool(name="feature_importance", ...),
    # 知识检索
    StructuredTool(name="search_knowledge", description="搜索汽车领域知识库",
                   args_schema=KnowledgeInput, func=retriever.invoke),
]
```

### 与 project1 的差异

| project1 | project2 |
|----------|----------|
| 前端传 `method: "correlation"` | 用户说"帮我看看相关性" → LLM 自动选 Tool |
| 加操作要改 step_executor + 前端 | 加一个 Tool 即可，前端无感 |
| 操作参数靠前端表单 | LLM 从用户自然语言中提取参数 |

## 六、RAG 系统

### 流程

```
用户输入 → Embedding → Chroma 向量搜索 → 召回 top-k 片段 → 注入 prompt → LLM 生成
```

### 模块

- **loader.py**：加载 YAML/PDF/TXT/Markdown 文档
- **splitter.py**：RecursiveCharacterTextSplitter 分块
- **embeddings.py**：默认 DeepSeek API（OpenAI 兼容），可配置其他模型
- **store.py**：Chroma 本地持久化
- **retriever.py**：LangChain `BaseRetriever` 接口

### 与 project1 TF-IDF 对比

| 维度 | project1 | project2 |
|------|----------|----------|
| 检索方式 | TF-IDF 关键词匹配 | 语义向量相似度 |
| 同义词 | "座椅" 召不回 "坐垫" | 语义理解，自然覆盖 |
| 文档处理 | 整篇读入，无分块 | 分块存储，精准定位 |
| 存储 | YAML + TXT 文件 | Chroma 向量库 |
| 接口 | 自定义 `KnowledgeBase.search()` | LangChain `BaseRetriever.invoke()` |

## 七、前后端适配

### 后端

project1 两个独立端点 → project2 一个统一流式端点：

```python
# project1
POST /api/analysis/plan        # 生成计划
POST /api/analysis/execute     # 执行步骤

# project2
POST /api/analysis/run/stream  # SSE 流，Graph 自动推进所有节点
```

### 前端 Analysis.vue

不再展示"步骤列表 + 点击执行"，改为 Graph 实时执行进度：

- 自动执行模式：Graph 一口气跑完
- 单步执行模式：每步人工确认后继续（利用 Graph interrupt）

## 八、生产级设计

### 8.1 错误处理与弹性

**Graph 层错误恢复**：

```python
# 每个节点包裹 try-except，不抛异常而是写入 state
def execute_step(state: AnalysisState) -> AnalysisState:
    try:
        result = run_tool(state)
        state["results"].append(result)
    except ToolTimeoutError:
        state["next_action"] = "retry"
        state["error_message"] = "操作超时，正在重试..."
    except DataQualityError as e:
        state["next_action"] = "replan"
        state["error_message"] = f"数据质量问题: {e}，重新规划..."
    except Exception as e:
        logger.exception("execute_step 未预期错误")
        state["next_action"] = "done"
        state["error_message"] = f"执行异常，已保存已完成步骤: {e}"
    return state
```

**LLM 调用重试**：所有 ChatModel 调用配置 `max_retries=3` + 指数退避：

```python
from langchain_core.runnables import RunnableConfig

model = ChatOpenAI(
    base_url=config.base_url,
    api_key=config.api_key,
    model=config.model,
    max_retries=3,
    timeout=60,          # 单次调用超时
    max_tokens=4096,
)
```

**Tool 执行超时**：每个 Tool 独立超时控制：

```python
tool = StructuredTool(
    name="train_regression",
    func=run_with_timeout(run_regression, timeout_seconds=120),
    ...
)
```

### 8.2 日志与可观测性

```python
# 结构化日志
import structlog

logger = structlog.get_logger()

# Graph 节点进入/退出自动打点
@traceable(name="execute_step")
def execute_step_node(state):
    logger.info("execute_step.start", step_index=state["current_step_index"])
    ...
    logger.info("execute_step.done", duration_ms=elapsed)

# LangSmith / LangFuse 追踪（配置开关）
# 开发环境默认关闭，生产环境通过环境变量启用
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 8.3 状态持久化与恢复

利用 LangGraph 的 SqliteSaver 持久化 Graph 状态，支持断点续跑：

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 生产环境用 SQLite，单文件、零配置、可靠
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

workflow = graph.compile(checkpointer=checkpointer)

# 配置中携带 thread_id，用于状态恢复
config = {"configurable": {"thread_id": project_id}}

# 如果上一次执行中断，resume 即可继续
# 支持用户关闭浏览器后重新打开，从上次断点继续
```

### 8.4 输入验证

所有 API 输入用 Pydantic v2 严格验证：

```python
from pydantic import BaseModel, Field, field_validator

class AnalysisRequest(BaseModel):
    project_id: str = Field(..., pattern=r'^[a-f0-9-]{36}$')
    user_input: str = Field(..., min_length=1, max_length=5000)

    @field_validator("user_input")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        # 防注入：去除危险字符，保留中英文和常用标点
        import re
        cleaned = re.sub(r'[<>{}]', '', v)
        if len(cleaned) < 1:
            raise ValueError("输入不能为空")
        return cleaned
```

### 8.5 资源管理

**DataFrame 生命周期**：大文件不常驻内存，按需加载/释放：

```python
class DataFrameCache:
    """LRU 缓存 DataFrame，避免重复加载大文件"""
    def __init__(self, max_size: int = 3):
        self._cache: OrderedDict[str, pd.DataFrame] = OrderedDict()
        self._max_size = max_size

    def get(self, project_id: str) -> pd.DataFrame:
        if project_id not in self._cache:
            df = load_and_merge(project_id)
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)  # 淘汰最久未用
            self._cache[project_id] = df
        return self._cache[project_id]

    def invalidate(self, project_id: str):
        self._cache.pop(project_id, None)
```

**连接池**：Chroma 向量库使用单例，避免重复初始化。

### 8.6 安全性

- **API Key**：不在代码/lognfig 中硬编码，优先读环境变量 `DEEPSEEK_API_KEY`，其次读 config.json
- **沙箱执行**：复用 engine/sandbox.py，用户自定义代码在隔离子进程运行
- **文件上传**：限制类型（csv/xlsx/json）、大小（100MB）、病毒扫描跳过（内网环境）
- **CORS**：生产环境配置白名单域名，不放开所有来源

### 8.7 优雅降级

```python
# RAG 不可用时，Agent 仍可工作（仅缺领域知识注入）
try:
    rag_context = retriever.invoke(user_input)
except RAGUnavailableError:
    logger.warning("RAG 不可用，跳过知识检索")
    rag_context = ""

# Embedding API 不可用时，回退到 TF-IDF（保留 project1 方案作为后备）
try:
    embeddings = get_embeddings()
except ConnectionError:
    logger.warning("Embedding API 不可用，回退到 TF-IDF")
    embeddings = TfidfFallback()
```

## 九、测试策略

### 9.1 测试分层与覆盖率目标

```
tests/
├── unit/                          # 覆盖率目标 ≥ 85%
│   ├── test_tools.py              # 每个 Tool 的输入/输出正确性
│   ├── test_nodes.py              # 每个 Graph 节点独立测试（mock LLM）
│   ├── test_rag.py                # RAG 检索/分块/向量化
│   └── test_state.py              # State 序列化/反序列化
├── integration/                   # 覆盖率目标 ≥ 70%
│   ├── test_workflow.py           # StateGraph 完整流程 + Checkpointer
│   └── test_api.py                # FastAPI 端点 + SSE 流（TestClient）
└── e2e/                           # 核心路径覆盖
    ├── test_analysis_flow.py      # 模拟完整分析对话
    └── test_error_recovery.py     # 模拟 LLM 超时/异常恢复
```

### 9.2 关键测试模式

```python
# LangGraph 的 Checkpointer 让工作流测试变得简单
from langgraph.checkpoint.memory import MemorySaver

def test_replan_on_low_r2():
    """R² < 0.3 时自动重新规划"""
    app = workflow.compile(checkpointer=MemorySaver())

    # 模拟一次失败执行
    state = {
        "user_input": "预测座椅满意度",
        "results": [{"type": "model", "metrics": {"r2": 0.15}}],
        "current_step_index": 1,
        ...
    }
    result = app.invoke(state, {"configurable": {"thread_id": "test-1"}})
    assert result["next_action"] == "replan"

def test_interrupt_resume():
    """人工确认断点：暂停 → 恢复"""
    app = workflow.compile(checkpointer=MemorySaver(), interrupt_before=["execute_step"])
    config = {"configurable": {"thread_id": "test-2"}}

    # 第一步：跑到 execute_step 前暂停
    result = app.invoke(initial_state, config)
    assert result["__interrupt__"] is not None

    # 用户确认后恢复
    result = app.invoke(None, config)  # None = 继续
    assert result["results"][0]["status"] == "done"
```

## 十一、启动方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（生产环境推荐）或 config.json
export DEEPSEEK_API_KEY=your_key
export DEEPSEEK_BASE_URL=https://your-instance/v1

# 3. 初始化 RAG 知识库
python scripts/init_rag.py

# 4. 启动后端
uvicorn backend.main:app --host 0.0.0.0 --port 8502 --workers 4

# 5. 构建并启动前端
cd frontend && npm run build && npm run preview
```

## 十二、对比文档结构

`docs/comparison.md`：

1. 项目概述
2. 架构对比（理论依据、分层设计）
3. 核心差异逐层对比
   - LLM 编排：手写 Agent vs LangChain AgentExecutor
   - 步骤调度：if-else vs StateGraph
   - 工具调用：手动字典分派 vs Tool Calling
   - 知识检索：TF-IDF vs RAG 语义搜索
   - 状态管理：手动 JSON vs Graph State + Checkpointer
   - 流式输出：手写 SSE vs astream_events
4. 代码量统计
5. 开发者体验（学习曲线、调试、扩展）
6. 总结与选型建议
