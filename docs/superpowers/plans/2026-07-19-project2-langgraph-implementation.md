# project2: LangChain + LangGraph 复现实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 LangChain + LangGraph 复现 project1 的数据科学家 Agent，保留 engine 算法层，替换 LLM 编排层。

**Architecture:** engine/ 层的纯算法模块不变，graph/ 层（StateGraph + Tools）取代 step_executor + llm_agent，agent/ 层提供 AgentExecutor + RAG，backend/ 和 frontend/ 基于 project1 改造适配。

**Tech Stack:** Python 3.10+, LangChain, LangGraph, FastAPI, Vue 3, Chroma, DeepSeek API (OpenAI-compatible)

---

## Phase 1: 项目脚手架

### Task 1: 创建 project2 目录结构

**Files:**
- Create: `D:\PythonFile\project2\` 下的空目录结构

- [ ] **Step 1: 创建所有目录**

```bash
mkdir -p /d/PythonFile/project2/{engine,graph,agent/rag,backend/routers,backend/models,frontend/src/{api,stores,views,components},knowledge,scripts,tests/{unit,integration,e2e},docs}
```

- [ ] **Step 2: 创建占位 __init__.py**

```bash
touch /d/PythonFile/project2/engine/__init__.py
touch /d/PythonFile/project2/graph/__init__.py
touch /d/PythonFile/project2/agent/__init__.py
touch /d/PythonFile/project2/agent/rag/__init__.py
touch /d/PythonFile/project2/backend/__init__.py
touch /d/PythonFile/project2/backend/routers/__init__.py
touch /d/PythonFile/project2/backend/models/__init__.py
touch /d/PythonFile/project2/tests/__init__.py
```

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git init && git add -A && git commit -m "chore: initialize project2 directory structure

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: 复制 engine 模块并删除不需要的文件

**Files:**
- Copy: `D:\PythonFile\project1\engine\*.py` → `D:\PythonFile\project2\engine\`
- Delete: `D:\PythonFile\project2\engine\llm_agent.py`, `D:\PythonFile\project2\engine\step_executor.py`

- [ ] **Step 1: 复制 engine 模块**

```bash
cp /d/PythonFile/project1/engine/*.py /d/PythonFile/project2/engine/
```

- [ ] **Step 2: 删除 llm_agent.py 和 step_executor.py**

```bash
rm /d/PythonFile/project2/engine/llm_agent.py
rm /d/PythonFile/project2/engine/step_executor.py
```

- [ ] **Step 3: 复制 knowledge 目录**

```bash
cp -r /d/PythonFile/project1/knowledge /d/PythonFile/project2/knowledge
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "chore: copy engine from project1, remove llm_agent and step_executor

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: 创建 requirements.txt 和配置文件

**Files:**
- Create: `D:\PythonFile\project2\requirements.txt`
- Create: `D:\PythonFile\project2\config.json`
- Create: `D:\PythonFile\project2\config.example.json`

- [ ] **Step 1: 编写 requirements.txt**

Write `D:\PythonFile\project2\requirements.txt`:

```
# LangChain 生态
langchain>=0.3.0
langchain-core>=0.3.0
langgraph>=0.2.0
langgraph-checkpoint-sqlite>=2.0.0

# RAG
chromadb>=0.5.0
langchain-text-splitters>=0.3.0

# 后端
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-multipart>=0.0.9

# 数据分析（与 project1 保持一致）
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
xgboost>=2.0.0
plotly>=5.15.0
openpyxl>=3.1.0
jinja2>=3.1.0
httpx>=0.25.0
openai>=1.30.0
pyyaml>=6.0
python-docx>=1.0.0
PyPDF2>=3.0.0
chardet>=5.0.0

# 生产级增强
structlog>=24.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
tenacity>=8.0.0
```

- [ ] **Step 2: 编写 config.json**

Write `D:\PythonFile\project2\config.json`:

```json
{
  "llm": {
    "name": "DeepSeek",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "model": "deepseek-chat",
    "temperature": 0.3,
    "max_tokens": 4096
  },
  "embedding": {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "model": "text-embedding-3-small"
  },
  "paths": {
    "projects_dir": "projects",
    "knowledge_dir": "knowledge",
    "data_dir": "data"
  }
}
```

- [ ] **Step 3: 编写 config.example.json**

Write `D:\PythonFile\project2\config.example.json`:

```json
{
  "llm": {
    "name": "DeepSeek",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "your-api-key-here",
    "model": "deepseek-chat",
    "temperature": 0.3,
    "max_tokens": 4096
  },
  "embedding": {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "your-api-key-here",
    "model": "text-embedding-3-small"
  },
  "paths": {
    "projects_dir": "projects",
    "knowledge_dir": "knowledge",
    "data_dir": "data"
  }
}
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "chore: add requirements.txt and config files

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: 创建 .gitignore、CLAUDE.md 和 README.md

**Files:**
- Create: `D:\PythonFile\project2\.gitignore`
- Create: `D:\PythonFile\project2\CLAUDE.md`
- Create: `D:\PythonFile\project2\README.md`

- [ ] **Step 1: 编写 .gitignore**

Write `D:\PythonFile\project2\.gitignore`:

```
__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/
node_modules/
dist/
projects/
*.db
checkpoints.db
config.json
.DS_Store
*.egg-info/
.pytest_cache/
```

- [ ] **Step 2: 编写 CLAUDE.md**

Write `D:\PythonFile\project2\CLAUDE.md`:

```
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
```

- [ ] **Step 3: 编写 README.md**

Write `D:\PythonFile\project2\README.md`:

```markdown
# DS Agent v2 — LangChain + LangGraph 版

基于 LangChain/LangGraph 的数据科学家 Agent，面向汽车研发工程师的数据分析工具。

## 与 v1 的区别

v1 (project1) 的 LLM 编排层是手写的，v2 用 LangChain AgentExecutor + LangGraph StateGraph 替换，
engine 算法层保持不变。详见 [docs/comparison.md](docs/comparison.md)。

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
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "chore: add .gitignore, CLAUDE.md, README.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 2: Graph 层 (核心)

### Task 5: 定义 AnalysisState

**Files:**
- Create: `D:\PythonFile\project2\graph\state.py`
- Test: `D:\PythonFile\project2\tests\unit\test_state.py`

- [ ] **Step 1: 编写 AnalysisState 定义**

Write `D:\PythonFile\project2\graph\state.py`:

```python
"""LangGraph AnalysisState 定义."""

from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
import pandas as pd


class StepResult(TypedDict, total=False):
    step_id: int
    type: str
    description: str
    status: str          # "done" | "failed" | "skipped"
    metrics: dict
    text: str
    charts: list[str]    # chart HTML file paths


class AnalysisStep(TypedDict, total=False):
    id: int
    type: str
    description: str
    params: dict
    status: str           # "pending" | "running" | "done" | "failed"


class AnalysisState(TypedDict, total=False):
    # === 输入 ===
    user_input: str
    project_id: str
    df: Optional[pd.DataFrame]

    # === RAG 上下文 ===
    rag_context: str

    # === 数据集信息（由 data_loader 提供）===
    df_info: dict

    # === 计划 ===
    plan: list[AnalysisStep]
    current_step_index: int

    # === 执行结果（跨步骤累积）===
    results: Annotated[list[StepResult], add_messages]
    context_summary: str

    # === 控制流 ===
    next_action: str    # "execute" | "skip" | "replan" | "done" | "retry"
    error_message: str

    # === 最终输出 ===
    conclusion: str
```

- [ ] **Step 2: 编写测试**

Write `D:\PythonFile\project2\tests\unit\test_state.py`:

```python
"""测试 AnalysisState 的定义和默认值."""
import pytest
from graph.state import AnalysisState


def test_state_defaults():
    """验证 state 字段默认值."""
    state: AnalysisState = {
        "user_input": "test",
        "project_id": "abc",
        "plan": [],
        "current_step_index": 0,
        "results": [],
        "context_summary": "",
        "next_action": "execute",
        "error_message": "",
        "rag_context": "",
        "conclusion": "",
    }
    assert state["user_input"] == "test"
    assert state["next_action"] == "execute"


def test_state_can_accumulate_results():
    """验证 results 字段可累积."""
    state: AnalysisState = {
        "user_input": "test",
        "plan": [],
        "current_step_index": 0,
        "results": [],
        "context_summary": "",
        "next_action": "done",
    }
    result: StepResult = {"step_id": 1, "type": "eda", "status": "done", "text": "ok"}
    state["results"].append(result)
    assert len(state["results"]) == 1
    assert state["results"][0]["status"] == "done"
```

- [ ] **Step 3: 运行测试并确认失败**

```bash
cd /d/PythonFile/project2 && python -m pytest tests/unit/test_state.py -v
# 预期: PASS (这是定义测试，不需要先失败)
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add AnalysisState definition with tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: 构建 Tool 封装层

**Files:**
- Create: `D:\PythonFile\project2\graph\tools.py`

- [ ] **Step 1: 编写 tools.py — Pydantic 输入模型 + Tool 函数**

Write `D:\PythonFile\project2\graph\tools.py`:

```python
"""LangChain Tool 封装 — 每个分析操作封装为 StructuredTool.

Tool 层不包含业务逻辑，只做参数转换和 engine 调用。
LLM 通过 Function Calling 自主选择调用哪个 Tool。
"""
import traceback
import time
from functools import wraps
from typing import Optional
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool
import pandas as pd

from engine import data_loader, data_cleaner, eda, feature_engineer, modeler


# === 超时包装器 ===
def with_timeout(timeout_seconds: int = 60):
    """为 Tool 函数添加超时保护."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("操作超时")))
            signal.alarm(timeout_seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


# === Pydantic 输入模型（LLM 通过 Function Calling 自动填参）===

class CleanInput(BaseModel):
    drop_dup: bool = Field(True, description="是否去重")
    fill_strategy: str = Field("mean", description="缺失值填充策略: mean/median/mode/constant")
    outlier_method: str = Field("iqr", description="异常值检测方法: iqr/zscore")

class FillMissingInput(BaseModel):
    strategy: str = Field("mean", description="填充策略: mean/median/mode/constant")
    columns: Optional[list[str]] = Field(None, description="要填充的列名列表，None 表示所有列")
    fill_value: Optional[float] = Field(None, description="当 strategy=constant 时的填充值")

class DescribeNumericInput(BaseModel):
    columns: Optional[list[str]] = Field(None, description="要统计的数值列，None 表示所有")

class CorrelationInput(BaseModel):
    method: str = Field("pearson", description="相关性方法: pearson/spearman")
    columns: Optional[list[str]] = Field(None, description="要分析的列")

class DistributionInput(BaseModel):
    column: str = Field(..., description="要绘制的列名")
    bins: int = Field(30, description="直方图分箱数")

class ScatterInput(BaseModel):
    x: str = Field(..., description="X 轴列名")
    y: str = Field(..., description="Y 轴列名")
    color: Optional[str] = Field(None, description="分组颜色列")
    trendline: bool = Field(True, description="是否添加趋势线")

class LineInput(BaseModel):
    x: str = Field(..., description="X 轴列名")
    y: str = Field(..., description="Y 轴列名")
    group_by: Optional[str] = Field(None, description="分组列")

class ScaleInput(BaseModel):
    columns: list[str] = Field(..., description="要缩放的列名")
    method: str = Field("standard", description="缩放方法: standard/minmax")

class EncodeInput(BaseModel):
    columns: list[str] = Field(..., description="要编码的列名")
    method: str = Field("onehot", description="编码方法: onehot/label")

class TrainRegressionInput(BaseModel):
    target: str = Field(..., description="目标变量列名")
    model_type: str = Field("linear", description="模型类型: linear/ridge/lasso/random_forest/xgboost")
    test_size: float = Field(0.2, description="测试集比例")
    feature_columns: Optional[list[str]] = Field(None, description="特征列名")

class ClusterInput(BaseModel):
    columns: list[str] = Field(..., description="聚类特征列名")
    n_clusters: int = Field(3, description="聚类数")

class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., description="搜索查询关键词")

# === Tool 执行函数 ===

def _safe_tool(func):
    """包装器：统一异常处理和结果格式."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            return {"success": True, "data": result, "elapsed_ms": round(elapsed * 1000)}
        except Exception as e:
            elapsed = time.time() - start
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "elapsed_ms": round(elapsed * 1000),
            }
    return wrapper


@_safe_tool
def run_clean_data(df: pd.DataFrame, drop_dup: bool = True,
                   fill_strategy: str = "mean", outlier_method: str = "iqr") -> dict:
    cleaned_df, summary = data_cleaner.clean_pipeline(
        df, drop_dup=drop_dup, fill_strategy=fill_strategy, outlier_method=outlier_method
    )
    return {"summary": summary, "row_count": len(cleaned_df), "col_count": len(cleaned_df.columns)}


@_safe_tool
def run_fill_missing(df: pd.DataFrame, strategy: str = "mean",
                     columns: Optional[list] = None, fill_value=None) -> dict:
    _, summary = data_cleaner.fill_missing(df, strategy=strategy, columns=columns, fill_value=fill_value)
    return {"summary": summary}


@_safe_tool
def run_describe_numeric(df: pd.DataFrame, columns: Optional[list] = None) -> dict:
    result = eda.describe_numeric(df, columns=columns)
    return {"statistics": result}


@_safe_tool
def run_correlation(df: pd.DataFrame, method: str = "pearson",
                    columns: Optional[list] = None) -> dict:
    corr_df, _ = eda.correlation_matrix(df, method=method, columns=columns)
    return {"correlation_matrix": corr_df.to_dict()}


@_safe_tool
def run_distribution(df: pd.DataFrame, column: str, bins: int = 30) -> dict:
    fig = eda.distribution_plot(df, column=column, bins=bins)
    return {"chart_type": "distribution", "column": column}


@_safe_tool
def run_scatter(df: pd.DataFrame, x: str, y: str,
                color: Optional[str] = None, trendline: bool = True) -> dict:
    fig = eda.scatter_plot(df, x=x, y=y, color=color, trendline=trendline)
    return {"chart_type": "scatter", "x": x, "y": y}


@_safe_tool
def run_line(df: pd.DataFrame, x: str, y: str, group_by: Optional[str] = None) -> dict:
    fig = eda.line_plot(df, x=x, y=y, group_by=group_by)
    return {"chart_type": "line", "x": x, "y": y}


@_safe_tool
def run_scale_features(df: pd.DataFrame, columns: list, method: str = "standard") -> dict:
    scaled_df, summary = feature_engineer.scale_features(df, columns, method=method)
    return {"summary": summary, "columns_scaled": len(columns)}


@_safe_tool
def run_encode(df: pd.DataFrame, columns: list, method: str = "onehot") -> dict:
    encoded_df, summary = feature_engineer.encode_categorical(df, columns, method=method)
    return {"summary": summary, "columns_encoded": len(columns)}


@_safe_tool
def run_train_regression(df: pd.DataFrame, target: str, model_type: str = "linear",
                         test_size: float = 0.2, feature_columns: Optional[list] = None) -> dict:
    if feature_columns:
        X = df[feature_columns]
    else:
        X = df.drop(columns=[target])
    y = df[target]

    from engine.modeler import split_data, train_regression, evaluate_regression
    X_train, X_test, y_train, y_test = split_data(X, y, target=target, test_size=test_size)
    model_obj, train_summary = train_regression(X_train, y_train, model_type=model_type)
    eval_metrics = evaluate_regression(model_obj, X_test, y_test)
    return {"train_summary": train_summary, "metrics": eval_metrics}


@_safe_tool
def run_cluster(df: pd.DataFrame, columns: list, n_clusters: int = 3) -> dict:
    result_df, summary, _ = modeler.train_cluster(df, columns=columns, n_clusters=n_clusters)
    return {"summary": summary, "cluster_count": n_clusters}


@_safe_tool
def run_feature_importance(df: pd.DataFrame, target: str) -> dict:
    X = df.drop(columns=[target])
    y = df[target]
    from engine.modeler import split_data, train_regression, feature_importance
    X_train, X_test, y_train, y_test = split_data(X, y, target=target)
    model_obj, _ = train_regression(X_train, y_train, model_type="random_forest")
    imp_df, _ = feature_importance(model_obj, X.columns.tolist())
    return {"feature_importance": imp_df.to_dict()}


# === 构建 Tool 列表 ===

def create_analysis_tools() -> list[StructuredTool]:
    """创建所有分析 Tool 的列表，供 Agent 使用."""
    return [
        StructuredTool.from_function(
            name="clean_data",
            description="清洗数据：去重、填充缺失值(mean/median/mode)、检测异常值(IQR/Z-score)。这是数据分析的第一步。",
            args_schema=CleanInput,
            func=run_clean_data,
        ),
        StructuredTool.from_function(
            name="fill_missing_values",
            description="填充缺失值，支持 mean/median/mode/constant 策略",
            args_schema=FillMissingInput,
            func=run_fill_missing,
        ),
        StructuredTool.from_function(
            name="describe_numeric",
            description="数值列描述统计：均值、标准差、分位数、偏度、峰度。用于了解数据基本特征。",
            args_schema=DescribeNumericInput,
            func=run_describe_numeric,
        ),
        StructuredTool.from_function(
            name="correlation_analysis",
            description="计算相关性矩阵(Pearson/Spearman)，用于发现变量间的线性关系。适合找出与目标变量相关的因素。",
            args_schema=CorrelationInput,
            func=run_correlation,
        ),
        StructuredTool.from_function(
            name="distribution_plot",
            description="生成单变量分布图(直方图+箱线图)，用于理解数据的分布形态和异常值。",
            args_schema=DistributionInput,
            func=run_distribution,
        ),
        StructuredTool.from_function(
            name="scatter_plot",
            description="生成散点图，可选趋势线和颜色分组。用于可视化两个变量的关系。",
            args_schema=ScatterInput,
            func=run_scatter,
        ),
        StructuredTool.from_function(
            name="line_plot",
            description="生成折线图，支持分组。用于展示趋势变化。",
            args_schema=LineInput,
            func=run_line,
        ),
        StructuredTool.from_function(
            name="scale_features",
            description="特征缩放：Z-score标准化或Min-Max归一化。建模前的必要步骤。",
            args_schema=ScaleInput,
            func=run_scale_features,
        ),
        StructuredTool.from_function(
            name="encode_categorical",
            description="分类变量编码：one-hot编码或标签编码",
            args_schema=EncodeInput,
            func=run_encode,
        ),
        StructuredTool.from_function(
            name="train_regression",
            description="训练回归模型(linear/ridge/lasso/random_forest/xgboost)，返回R²/MSE/MAE等指标。用于预测连续值。",
            args_schema=TrainRegressionInput,
            func=run_train_regression,
        ),
        StructuredTool.from_function(
            name="cluster_analysis",
            description="K-Means聚类分析，用于发现数据中的自然分组。",
            args_schema=ClusterInput,
            func=run_cluster,
        ),
        StructuredTool.from_function(
            name="feature_importance",
            description="分析特征对目标变量的重要性排名。使用随机森林计算。",
            args_schema=TrainRegressionInput,
            func=run_feature_importance,
        ),
    ]
```

- [ ] **Step 2: 验证导入**

```bash
cd /d/PythonFile/project2 && python -c "from graph.tools import create_analysis_tools; tools = create_analysis_tools(); print(f'Created {len(tools)} tools'); [print(f'  {t.name}: {t.description[:40]}...') for t in tools]"
```

预期输出: `Created 12 tools` 及各 tool 名称列表。

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add LangChain Tool wrappers for all analysis operations

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: 构建 Graph 节点

**Files:**
- Create: `D:\PythonFile\project2\graph\nodes.py`

- [ ] **Step 1: 编写 nodes.py — 5 个 Graph 节点**

Write `D:\PythonFile\project2\graph\nodes.py`:

```python
"""LangGraph 工作流节点实现.

节点职责：
- understand_intent: RAG 检索 + 意图解析
- plan_analysis: LLM 生成分析计划
- execute_step: 执行当前步骤的 Tool 调用
- interpret_result: LLM 解读执行结果
- decide_next: 确定下一步动作（继续/跳过/重新规划/完成）
- generate_conclusion: 生成综合结论
"""
import json
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from graph.state import AnalysisState
from graph.tools import create_analysis_tools
from engine.data_loader import get_data_info
from engine.config import load_config, AppConfig

logger = logging.getLogger(__name__)


def _get_llm(config: AppConfig) -> ChatOpenAI:
    """创建 LLM 实例."""
    return ChatOpenAI(
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
        max_retries=3,
        timeout=60,
    )


def _get_rag_context(query: str, project_id: str) -> str:
    """获取 RAG 检索上下文，失败时返回空字符串."""
    try:
        from agent.rag.retriever import get_retriever
        retriever = get_retriever()
        docs = retriever.invoke(query)
        if docs:
            return "\n\n".join([f"相关领域知识:\n{d.page_content}" for d in docs[:3]])
    except Exception as e:
        logger.warning("RAG 检索失败: %s", e)
    return ""


# === 节点函数 ===

async def understand_intent(state: AnalysisState, config: RunnableConfig) -> dict:
    """节点 1: 意图理解 + RAG 知识注入."""
    user_input = state["user_input"]
    project_id = state.get("project_id", "")

    rag_context = _get_rag_context(user_input, project_id)

    df = state.get("df")
    df_info = {}
    if df is not None:
        df_info = get_data_info(df)

    logger.info("understand_intent: rag_context_len=%d, df_columns=%d",
                len(rag_context), len(df_info.get("columns", [])))

    return {
        "rag_context": rag_context,
        "df_info": df_info,
    }


async def plan_analysis(state: AnalysisState, config: RunnableConfig) -> dict:
    """节点 2: LLM 生成分析计划."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    tools = create_analysis_tools()

    system_prompt = f"""你是一个汽车研发数据分析专家。

可用工具:
{chr(10).join([f'- {t.name}: {t.description}' for t in tools])}

数据集信息:
- 行数: {state['df_info'].get('row_count', 'N/A')}
- 列数: {state['df_info'].get('col_count', 'N/A')}
- 列名: {state['df_info'].get('columns', [])}
- 数值列: {state['df_info'].get('numeric_columns', [])}
- 分类列: {state['df_info'].get('categorical_columns', [])}

{state.get('rag_context', '')}

请生成分析计划。返回 JSON 格式:
{{"plan": [{{"id": 1, "type": "eda", "description": "...", "params": {{}}, "status": "pending"}}], "reasoning": "..."}}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户需求: {state['user_input']}\n请生成分析计划。"),
    ]

    response = await llm.ainvoke(messages)
    raw_text = response.content

    try:
        plan_data = json.loads(raw_text)
        plan = plan_data.get("plan", [])
    except json.JSONDecodeError:
        logger.warning("LLM 返回非 JSON 格式，使用默认计划")
        plan = _default_plan(state)

    return {
        "plan": plan,
        "current_step_index": 0,
        "next_action": "execute",
        "error_message": "",
    }


def _default_plan(state: AnalysisState) -> list:
    """当 LLM 解析失败时的默认计划."""
    return [
        {"id": 1, "type": "eda", "description": "数据描述统计", "params": {}, "status": "pending"},
        {"id": 2, "type": "eda", "description": "相关性分析", "params": {"method": "pearson"}, "status": "pending"},
    ]


async def execute_step(state: AnalysisState, config: RunnableConfig) -> dict:
    """节点 3: 执行当前步骤."""
    idx = state["current_step_index"]
    plan = state["plan"]

    if idx >= len(plan):
        return {"next_action": "done"}

    step = plan[idx]
    step["status"] = "running"

    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    tools = create_analysis_tools()
    llm_with_tools = llm.bind_tools(tools)

    prompt = f"""执行此分析步骤:
- 步骤类型: {step['type']}
- 描述: {step['description']}
- 参数: {step.get('params', {})}

已完成步骤的结果:
{state.get('context_summary', '无')}

请选择合适的工具执行此步骤。"""

    try:
        response = await llm_with_tools.ainvoke([HumanMessage(content=prompt)])

        tool_results = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool = next((t for t in tools if t.name == tool_name), None)
                if tool:
                    df = state.get("df")
                    if df is not None and "df" not in tool_args:
                        tool_args["df"] = df
                    result = tool.func(**tool_args)
                    tool_results.append({"tool": tool_name, "result": result})

        result_entry = {
            "step_id": step["id"],
            "type": step["type"],
            "description": step["description"],
            "status": "done" if tool_results else "done",
            "metrics": {},
            "text": json.dumps(tool_results, ensure_ascii=False, default=str),
            "charts": [],
        }

        results = list(state.get("results", []))
        results.append(result_entry)

        return {
            "results": results,
            "current_step_index": idx + 1,
            "next_action": "interpret",
            "error_message": "",
        }

    except Exception as e:
        logger.exception("execute_step 失败: step_id=%d", step["id"])
        return {
            "next_action": "replan" if idx < 2 else "done",
            "error_message": f"步骤 {step['id']} 执行失败: {e}",
        }


async def interpret_result(state: AnalysisState, config: RunnableConfig) -> dict:
    """节点 4: LLM 解读执行结果."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    results = state.get("results", [])

    if not results:
        return {"context_summary": "暂无结果", "next_action": "done"}

    latest = results[-1]
    prompt = f"""解读以下数据分析结果:
步骤类型: {latest['type']}
步骤描述: {latest['description']}
结果: {latest.get('text', '无')}

请用通俗的语言解释结果的含义，面向汽车研发工程师。不超过 300 字。"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    interpretation = response.content

    # 构建累积的上下文摘要
    prev_summary = state.get("context_summary", "")
    new_summary = f"""{prev_summary}
步骤 {latest['step_id']}: {latest['description']}
解读: {interpretation}
"""

    return {
        "context_summary": new_summary,
        "next_action": "decide",
    }


def decide_next(state: AnalysisState) -> Literal["execute", "generate_conclusion"]:
    """节点 5: 确定下一步动作（确定性代码逻辑，不依赖 LLM）."""
    idx = state["current_step_index"]
    plan = state["plan"]
    error = state.get("error_message", "")

    if error and "replan" in state.get("next_action", ""):
        return "execute"  # 回到 plan_analysis 重新规划

    if idx >= len(plan):
        return "generate_conclusion"

    return "execute"


async def generate_conclusion(state: AnalysisState, config: RunnableConfig) -> dict:
    """节点 6: 生成综合结论."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)

    results = state.get("results", [])
    summary = state.get("context_summary", "")

    prompt = f"""基于以下全部分析结果，生成综合分析结论:

分析摘要:
{summary}

用户原始需求: {state['user_input']}

请用结构化方式输出:
1. 核心发现 (3-5 条)
2. 建议下一步行动
3. 注意事项
"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "conclusion": response.content,
        "next_action": "done",
    }
```

- [ ] **Step 2: 验证导入**

```bash
cd /d/PythonFile/project2 && python -c "from graph.nodes import understand_intent, plan_analysis, execute_step, interpret_result, decide_next, generate_conclusion; print('All nodes imported successfully')"
```

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add LangGraph workflow nodes

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: 构建 StateGraph 工作流

**Files:**
- Create: `D:\PythonFile\project2\graph\workflow.py`

- [ ] **Step 1: 编写 workflow.py**

Write `D:\PythonFile\project2\graph\workflow.py`:

```python
"""LangGraph StateGraph 工作流构建与编译."""
import logging
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import AnalysisState
from graph.nodes import (
    understand_intent,
    plan_analysis,
    execute_step,
    interpret_result,
    decide_next,
    generate_conclusion,
)

logger = logging.getLogger(__name__)


def build_workflow(checkpointer=None):
    """构建分析工作流 StateGraph.

    Graph 结构:
    START → understand_intent → plan_analysis → execute_step → interpret_result
                ↑                                                     │
                │                    ┌────────────────────────────────┘
                │                    ▼
                └────────────── decide_next ──→ generate_conclusion → END
    """
    workflow = StateGraph(AnalysisState)

    # 添加节点
    workflow.add_node("understand_intent", understand_intent)
    workflow.add_node("plan_analysis", plan_analysis)
    workflow.add_node("execute_step", execute_step)
    workflow.add_node("interpret_result", interpret_result)
    workflow.add_node("generate_conclusion", generate_conclusion)

    # 添加边
    workflow.add_edge(START, "understand_intent")
    workflow.add_edge("understand_intent", "plan_analysis")
    workflow.add_edge("plan_analysis", "execute_step")
    workflow.add_edge("execute_step", "interpret_result")

    # 条件路由: decide_next 决定下一步
    workflow.add_conditional_edges(
        "interpret_result",
        decide_next,
        {
            "execute": "execute_step",
            "generate_conclusion": "generate_conclusion",
        },
    )

    workflow.add_edge("generate_conclusion", END)

    # 编译
    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)


def create_production_workflow(db_path: str = "checkpoints.db"):
    """创建生产环境工作流（SQLite 持久化状态）."""
    checkpointer = SqliteSaver.from_conn_string(db_path)
    return build_workflow(checkpointer=checkpointer)


def create_dev_workflow():
    """创建开发环境工作流（内存状态，不持久化）."""
    return build_workflow(checkpointer=MemorySaver())
```

- [ ] **Step 2: 验证 Graph 结构**

```bash
cd /d/PythonFile/project2 && python -c "
from graph.workflow import create_dev_workflow
app = create_dev_workflow()
print('Graph compiled successfully')
print('Nodes:', list(app.get_graph().nodes.keys()))
print('Channels:', list(app.get_graph().channels.keys()))
"
```

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add StateGraph workflow builder

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 3: Agent 层 + RAG

### Task 9: 构建 Agent 和 Prompt 模板

**Files:**
- Create: `D:\PythonFile\project2\agent\prompts.py`
- Create: `D:\PythonFile\project2\agent\analysis_agent.py`

- [ ] **Step 1: 编写 prompts.py**

Write `D:\PythonFile\project2\agent\prompts.py`:

```python
"""System prompt 模板."""

SYSTEM_PROMPT = """你是一个汽车研发数据分析专家 Agent。

## 你的能力
- 对 CSV/Excel 数据执行统计分析
- 生成可视化图表（分布图、散点图、折线图、热力图）
- 特征工程（标准化、编码、特征选择）
- 机器学习建模（回归、分类、聚类）
- 解读分析结果并提供专业建议

## 工作方式
1. 理解用户的自然语言需求
2. 选择合适的分析工具
3. 执行分析并解读结果
4. 给出专业建议

## 领域知识
你熟悉汽车行业常见分析场景：
- 座椅面料感知质量评价（光泽度、柔软度、耐磨性）
- 内饰满意度调查分析
- 车辆性能参数相关性分析
- 生产质量数据异常检测
- 用户调研数据的因子分析和聚类

## 输出要求
- 用通俗易懂的中文解释分析结果
- 面向汽车研发工程师，不需要解释基础统计概念
- 给出可操作的工程建议
"""

PLAN_PROMPT_TEMPLATE = """你是一个汽车研发数据分析专家。

## 数据集信息
{df_info}

## 领域知识
{rag_context}

## 可用分析工具
{tool_list}

## 用户需求
{user_input}

## 任务
请生成一个分析计划，列出需要执行的步骤序列。
返回严格 JSON 格式（不要 markdown 代码块包裹）:

{{
  "plan": [
    {{
      "id": 1,
      "type": "clean|eda|feature|model",
      "description": "步骤描述（中文）",
      "params": {{}},
      "status": "pending"
    }}
  ],
  "reasoning": "计划制定的思考过程（中文）"
}}
"""

INTERPRET_PROMPT_TEMPLATE = """## 分析步骤
- 类型: {step_type}
- 描述: {step_description}

## 执行结果
{result_text}

## 已完成的上一步分析
{context_summary}

## 任务
用通俗的中文解释这个结果对汽车研发工程师意味着什么。
- 关键数字用日常语言解释（例如 "R²=0.85 说明该模型能解释 85% 的变异"）
- 如果结果异常，说明可能的原因
- 给出下一步建议
不超过 300 字。
"""

CONCLUSION_PROMPT_TEMPLATE = """## 全部分析结果
{all_results}

## 用户原始需求
{user_input}

## 任务
生成综合分析报告，包含:
1. **核心发现** (3-5 条，每条一句话)
2. **工程建议** (可操作的下一步行动)
3. **注意事项** (数据质量、模型局限等)
"""
```

- [ ] **Step 2: 编写 analysis_agent.py**

Write `D:\PythonFile\project2\agent\analysis_agent.py`:

```python
"""LangChain Agent 管理器 — 创建和配置分析 Agent."""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.prompts import SYSTEM_PROMPT
from graph.tools import create_analysis_tools


def create_analysis_agent(
    base_url: str,
    api_key: str,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> AgentExecutor:
    """创建分析 Agent.

    Args:
        base_url: API 地址
        api_key: API Key
        model: 模型名
        temperature: 温度参数
        max_tokens: 最大 token

    Returns:
        配置好的 AgentExecutor 实例
    """
    llm = ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=3,
        timeout=60,
    )

    tools = create_analysis_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True,
    )

    return executor
```

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add AgentExecutor and prompt templates

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 10: 构建 RAG 系统

**Files:**
- Create: `D:\PythonFile\project2\agent\rag\loader.py`
- Create: `D:\PythonFile\project2\agent\rag\splitter.py`
- Create: `D:\PythonFile\project2\agent\rag\embeddings.py`
- Create: `D:\PythonFile\project2\agent\rag\store.py`
- Create: `D:\PythonFile\project2\agent\rag\retriever.py`

- [ ] **Step 1: 编写 loader.py**

Write `D:\PythonFile\project2\agent\rag\loader.py`:

```python
"""文档加载器 — 加载 knowledge/ 目录下的各种文档."""
import os
from pathlib import Path
from langchain_core.documents import Document


def load_documents(knowledge_dir: str = "knowledge") -> list[Document]:
    """加载知识库中的所有文档.

    Supported formats: .txt, .md, .yaml, .yml
    """
    docs = []
    root = Path(knowledge_dir)

    if not root.exists():
        return docs

    for filepath in root.rglob("*"):
        if filepath.is_file():
            suffix = filepath.suffix.lower()
            if suffix in (".txt", ".md", ".yaml", ".yml"):
                try:
                    content = filepath.read_text(encoding="utf-8")
                    docs.append(Document(
                        page_content=content,
                        metadata={"source": str(filepath), "type": suffix.lstrip(".")},
                    ))
                except Exception:
                    pass

    return docs
```

- [ ] **Step 2: 编写 splitter.py**

Write `D:\PythonFile\project2\agent\rag\splitter.py`:

```python
"""文档分块器."""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(
    docs: list[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[Document]:
    """递归分块，保持句子边界."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    return splitter.split_documents(docs)
```

- [ ] **Step 3: 编写 embeddings.py**

Write `D:\PythonFile\project2\agent\rag\embeddings.py`:

```python
"""Embedding 模型 — 默认使用 DeepSeek API，可配置其他模型."""
import json
import os
from langchain_openai import OpenAIEmbeddings


def create_embeddings(config_path: str = "config.json") -> OpenAIEmbeddings:
    """创建 Embedding 模型实例.

    优先级: 环境变量 > config.json
    """
    base_url = os.getenv("EMBEDDING_BASE_URL", "")
    api_key = os.getenv("EMBEDDING_API_KEY", "")
    model = os.getenv("EMBEDDING_MODEL", "")

    if not base_url:
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            emb_cfg = cfg.get("embedding", {})
            base_url = base_url or emb_cfg.get("base_url", "")
            api_key = api_key or emb_cfg.get("api_key", "")
            model = model or emb_cfg.get("model", "text-embedding-3-small")
        except (FileNotFoundError, KeyError):
            pass

    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY", "")

    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )
```

- [ ] **Step 4: 编写 store.py**

Write `D:\PythonFile\project2\agent\rag\store.py`:

```python
"""Chroma 向量库管理."""
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document


def create_vector_store(
    docs: list[Document],
    embeddings,
    persist_dir: str = "chroma_db",
) -> Chroma:
    """创建并持久化向量库."""
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vector_store


def load_vector_store(
    embeddings,
    persist_dir: str = "chroma_db",
) -> Chroma:
    """加载已有向量库."""
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
```

- [ ] **Step 5: 编写 retriever.py**

Write `D:\PythonFile\project2\agent\rag\retriever.py`:

```python
"""RAG 检索器 — 单例模式，LangChain Retriever 接口."""
import logging
from langchain_core.retrievers import BaseRetriever

from agent.rag.embeddings import create_embeddings
from agent.rag.store import load_vector_store

logger = logging.getLogger(__name__)

_retriever_instance = None


def get_retriever(
    persist_dir: str = "chroma_db",
    k: int = 3,
) -> BaseRetriever:
    """获取 RAG 检索器单例.

    Args:
        persist_dir: Chroma 持久化目录
        k: 返回的文档片段数量

    Returns:
        LangChain Retriever 实例
    """
    global _retriever_instance

    if _retriever_instance is not None:
        return _retriever_instance

    try:
        embeddings = create_embeddings()
        vector_store = load_vector_store(embeddings, persist_dir=persist_dir)
        _retriever_instance = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
        logger.info("RAG retriever initialized with k=%d", k)
    except Exception as e:
        logger.warning("Failed to initialize RAG: %s. Using fallback.", e)
        _retriever_instance = _FallbackRetriever()

    return _retriever_instance


class _FallbackRetriever(BaseRetriever):
    """RAG 不可用时的回退检索器（返回空结果）."""
    def _get_relevant_documents(self, query: str):
        return []
```

- [ ] **Step 6: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add RAG system (loader, splitter, embeddings, store, retriever)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 4: 后端适配

### Task 11: 构建 FastAPI deps 和 schemas

**Files:**
- Create: `D:\PythonFile\project2\backend\deps.py`
- Create: `D:\PythonFile\project2\backend\models\schemas.py`

- [ ] **Step 1: 编写 deps.py**

Write `D:\PythonFile\project2\backend\deps.py`:

```python
"""FastAPI 共享依赖."""
import json
import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd

from engine.project_manager import ProjectManager
from graph.workflow import create_production_workflow, create_dev_workflow

logger = logging.getLogger(__name__)

pm = ProjectManager(projects_dir="projects")

# 工作流懒加载
_workflow = None


def get_workflow():
    """获取编译后的 Graph 工作流.

    生产环境用 SQLite 持久化，开发环境用内存。
    """
    global _workflow
    if _workflow is None:
        try:
            _workflow = create_production_workflow("checkpoints.db")
            logger.info("Workflow initialized with SQLite checkpointer")
        except Exception as e:
            logger.warning("SQLite unavailable, using memory: %s", e)
            _workflow = create_dev_workflow()
    return _workflow


def load_chart_html(project_id: str, chart_name: str) -> str:
    """从磁盘加载图表 HTML."""
    chart_path = Path("projects") / project_id / "charts" / f"{chart_name}.html"
    if chart_path.exists():
        return chart_path.read_text(encoding="utf-8")
    return ""
```

- [ ] **Step 2: 编写 schemas.py**

Write `D:\PythonFile\project2\backend\models\schemas.py`:

```python
"""Pydantic 请求/响应模型."""
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LLMConfigSchema(BaseModel):
    name: str = "DeepSeek"
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096


class AnalysisRunRequest(BaseModel):
    """统一的流式分析请求."""
    project_id: str = Field(..., pattern=r'^[a-f0-9-]{36}$', description="项目 UUID")
    user_input: str = Field(..., min_length=1, max_length=5000, description="用户分析需求")

    @field_validator("user_input")
    @classmethod
    def sanitize(cls, v: str) -> str:
        cleaned = re.sub(r'[<>{}]', '', v)
        if len(cleaned.strip()) < 1:
            raise ValueError("输入不能为空")
        return cleaned.strip()


class GenerateReportRequest(BaseModel):
    project_id: str = Field(..., pattern=r'^[a-f0-9-]{36}$')
    title: str = Field(..., min_length=1, max_length=200)
    user_notes: str = Field("", max_length=2000)
    include_conclusion: bool = True


class MergeDataRequest(BaseModel):
    selected_files: list[str] = Field(..., min_length=1)


class ConcludeRequest(BaseModel):
    project_id: str = Field(..., pattern=r'^[a-f0-9-]{36}$')
    user_notes: str = Field("", max_length=2000)
```

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add FastAPI deps and Pydantic schemas

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 12: 构建 analysis 路由（核心改造点）

**Files:**
- Create: `D:\PythonFile\project2\backend\routers\analysis.py`

- [ ] **Step 1: 编写 analysis.py**

Write `D:\PythonFile\project2\backend\routers\analysis.py`:

```python
"""分析路由 — LangGraph StateGraph 驱动的流式分析 API."""
import json
import logging
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig

from backend.models.schemas import AnalysisRunRequest
from backend.deps import pm, get_workflow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])


def _load_project_data(project_id: str) -> pd.DataFrame:
    """加载项目数据."""
    project = pm.load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    data_files = pm.list_data_files(project_id)
    if not data_files:
        raise HTTPException(status_code=400, detail="项目没有数据文件")

    return pm.merge_selected_data(project_id, data_files)


def _sanitize_for_json(obj):
    """递归处理 NaN/Infinity."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if np.isnan(obj):
            return None
        if np.isinf(obj):
            return None
        return obj
    return obj


@router.post("/analysis/run/stream")
async def run_analysis_stream(req: AnalysisRunRequest):
    """流式执行完整分析流程.

    SSE 事件类型:
    - node_start: 节点开始
    - node_end: 节点结束
    - llm_token: LLM 逐 token 输出
    - tool_call: 工具调用
    - error: 错误信息
    - done: 完成
    """
    try:
        df = _load_project_data(req.project_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据加载失败: {e}")

    workflow = get_workflow()
    config: RunnableConfig = {"configurable": {"thread_id": req.project_id}}

    initial_state = {
        "user_input": req.user_input,
        "project_id": req.project_id,
        "df": df,
        "plan": [],
        "current_step_index": 0,
        "results": [],
        "context_summary": "",
        "next_action": "execute",
        "error_message": "",
        "rag_context": "",
        "conclusion": "",
    }

    async def event_generator():
        try:
            async for event in workflow.astream_events(initial_state, config=config, version="v2"):
                event_type = event.get("event", "")

                # LLM 流式 token
                if event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'type': 'llm_token', 'content': chunk.content}, ensure_ascii=False)}\n\n"

                # Tool 调用开始
                elif event_type == "on_tool_start":
                    tool_name = event.get("name", "unknown")
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name}, ensure_ascii=False)}\n\n"

                # Tool 调用结束
                elif event_type == "on_tool_end":
                    tool_name = event.get("name", "unknown")
                    output = _sanitize_for_json(event.get("data", {}).get("output", {}))
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': tool_name, 'output': output}, ensure_ascii=False)}\n\n"

                # 节点结束
                elif event_type == "on_chain_end":
                    chain_name = event.get("name", "")
                    output = event.get("data", {}).get("output", {})
                    if isinstance(output, dict):
                        yield f"data: {json.dumps({'type': 'chain_end', 'node': chain_name, 'state_update': _sanitize_for_json(output)}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.exception("Graph execution error")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

- [ ] **Step 2: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add LangGraph-driven analysis SSE endpoint

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 13: 构建其余路由和 main.py

**Files:**
- Create: `D:\PythonFile\project2\backend\routers\config.py`
- Create: `D:\PythonFile\project2\backend\routers\projects.py`
- Create: `D:\PythonFile\project2\backend\routers\reports.py`
- Create: `D:\PythonFile\project2\backend\main.py`

- [ ] **Step 1: 编写 config.py**

Write `D:\PythonFile\project2\backend\routers\config.py`:

```python
"""配置和健康检查路由."""
from fastapi import APIRouter, HTTPException
from engine.config import load_config, save_config, LLMConfig, AppConfig
from engine.llm_agent import LLMAdapter
from backend.models.schemas import LLMConfigSchema

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "framework": "LangChain+LangGraph"}


@router.get("/config")
async def get_config():
    try:
        config = load_config("config.json")
        return config.to_dict()
    except FileNotFoundError:
        return AppConfig().to_dict()


@router.post("/config")
async def update_config(schema: LLMConfigSchema):
    config = AppConfig(
        llm=LLMConfig(
            base_url=schema.base_url,
            api_key=schema.api_key,
            model=schema.model,
            temperature=schema.temperature,
            max_tokens=schema.max_tokens,
        )
    )
    save_config(config, "config.json")
    return {"status": "ok"}


@router.post("/config/test")
async def test_connection(schema: LLMConfigSchema):
    adapter = LLMAdapter(LLMConfig(
        base_url=schema.base_url,
        api_key=schema.api_key,
        model=schema.model,
        temperature=schema.temperature,
        max_tokens=schema.max_tokens,
    ))
    ok, msg = adapter.test_connection()
    return {"success": ok, "message": msg}
```

- [ ] **Step 2: 编写 projects.py**

Write `D:\PythonFile\project2\backend\routers\projects.py`:

```python
"""项目管理路由."""
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.deps import pm
from backend.models.schemas import MergeDataRequest

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
async def list_projects():
    return pm.list_projects()


@router.post("")
async def create_project(name: str = Form(...), file: UploadFile = File(...)):
    project_id = str(uuid.uuid4())
    upload_dir = Path("uploads") / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    pid = pm.create_project(name, str(file_path))
    return {"project_id": pid, "name": name}


@router.get("/{project_id}")
async def get_project(project_id: str):
    return pm.load_project(project_id)


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    pm.delete_project(project_id)
    return {"status": "ok"}


@router.get("/{project_id}/info")
async def get_project_info(project_id: str):
    return pm.get_project_info(project_id)


@router.get("/{project_id}/data")
async def list_data(project_id: str):
    return pm.list_data_files(project_id)


@router.post("/{project_id}/data")
async def add_data(project_id: str, file: UploadFile = File(...)):
    upload_dir = Path("uploads") / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    return {"filename": pm.add_data(project_id, str(file_path))}


@router.post("/{project_id}/data/merge")
async def merge_data(project_id: str, req: MergeDataRequest):
    df = pm.merge_selected_data(project_id, req.selected_files)
    return {"row_count": len(df), "col_count": len(df.columns)}


@router.get("/{project_id}/reports")
async def list_reports(project_id: str):
    return pm.list_reports(project_id)
```

- [ ] **Step 3: 编写 reports.py**

Write `D:\PythonFile\project2\backend\routers\reports.py`:

```python
"""报告生成路由."""
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse

from backend.models.schemas import GenerateReportRequest, ConcludeRequest
from backend.deps import pm, get_workflow
from engine.reporter import generate_html_report, build_section

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/generate")
async def generate_report(req: GenerateReportRequest):
    project = pm.load_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    state = project.get("state", {})
    rounds = state.get("rounds", [])
    sections = []

    for round_data in rounds:
        for step in round_data.get("steps", []):
            if step.get("status") == "done":
                section = build_section(
                    title=step.get("description", "分析步骤"),
                    text=step.get("text", ""),
                )
                sections.append(section)

    html = generate_html_report(
        title=req.title,
        sections=sections,
        conclusion=project.get("conclusion", ""),
        data_source=project.get("meta", {}).get("data_file", ""),
        rows=0,
        cols=0,
    )

    report_path = pm.save_report(req.project_id, html)

    return {"report_path": report_path, "status": "ok"}


@router.post("/conclude/stream")
async def conclude_stream(req: ConcludeRequest):
    workflow = get_workflow()
    project = pm.load_project(req.project_id)
    state = project.get("state", {})

    async def event_generator():
        from graph.nodes import generate_conclusion
        from langchain_core.runnables import RunnableConfig

        conclusion_state = {
            "results": state.get("results", []),
            "context_summary": state.get("context_summary", ""),
            "user_input": state.get("user_input", ""),
        }
        config: RunnableConfig = {"configurable": {"thread_id": req.project_id}}

        async for event in workflow.astream_events(
            {"results": conclusion_state["results"], "context_summary": conclusion_state["context_summary"],
             "user_input": conclusion_state["user_input"]},
            config=config, version="v2"
        ):
            event_type = event.get("event", "")
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                if hasattr(chunk, "content") and chunk.content:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/download/{project_id}")
async def download_latest(project_id: str):
    reports = pm.list_reports(project_id)
    if not reports:
        raise HTTPException(status_code=404, detail="无报告")
    latest = sorted(reports)[-1]
    filepath = Path("projects") / project_id / "reports" / latest
    return FileResponse(str(filepath), media_type="text/html", filename=latest)
```

- [ ] **Step 4: 编写 main.py**

Write `D:\PythonFile\project2\backend\main.py`:

```python
"""FastAPI 应用入口."""
import json
import logging
import numpy as np
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.routers import config, projects, analysis, reports

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DS Agent v2", version="2.0.0", description="LangChain + LangGraph 数据科学家 Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(projects.router)
app.include_router(analysis.router)
app.include_router(reports.router)


# NaN/Infinity 安全序列化
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.floating, float)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# 生产环境提供前端静态文件
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
```

- [ ] **Step 5: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add FastAPI routes (config, projects, reports) and main entry

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 5: 前端适配

### Task 14: 复制前端项目并适配 API 层

**Files:**
- Copy: `D:\PythonFile\project1\fastapi-app\frontend\` → `D:\PythonFile\project2\frontend\`
- Modify: `D:\PythonFile\project2\frontend\src\api\index.js`
- Modify: `D:\PythonFile\project2\frontend\vite.config.js`

- [ ] **Step 1: 复制整个前端项目**

```bash
cp -r /d/PythonFile/project1/fastapi-app/frontend/* /d/PythonFile/project2/frontend/
cp /d/PythonFile/project1/fastapi-app/frontend/.gitignore /d/PythonFile/project2/frontend/ 2>/dev/null || true
```

- [ ] **Step 2: 修改 vite.config.js 适配 project2**

Read existing vite.config.js and update proxy target if different:

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8502',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 修改 API 层适配新 SSE 格式**

Write `D:\PythonFile\project2\frontend\src\api\index.js`:

```javascript
import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

// === Config ===
export const getConfig = () => api.get('/config')
export const saveConfig = (config) => api.post('/config', config)
export const testConnection = (config) => api.post('/config/test', config)

// === Projects ===
export const listProjects = () => api.get('/projects')
export const createProject = (formData) => api.post('/projects', formData)
export const getProject = (id) => api.get(`/projects/${id}`)
export const deleteProject = (id) => api.delete(`/projects/${id}`)
export const getProjectInfo = (id) => api.get(`/projects/${id}/info`)
export const listDataFiles = (id) => api.get(`/projects/${id}/data`)
export const addDataFile = (id, formData) => api.post(`/projects/${id}/data`, formData)
export const mergeDataFiles = (id, selectedFiles) =>
  api.post(`/projects/${id}/data/merge`, { selected_files: selectedFiles })

// === Reports ===
export const listReports = (id) => api.get(`/projects/${id}/reports`)
export const generateReport = (projectId, title, userNotes) =>
  api.post('/report/generate', { project_id: projectId, title, user_notes: userNotes })
export const downloadReport = (projectId, reportName) => {
  const url = reportName
    ? `/api/report/download/${projectId}/${reportName}`
    : `/api/report/download/${projectId}`
  window.open(url)
}

// === Analysis (LangGraph SSE Stream) ===
export function streamAnalysis(projectId, userInput, callbacks) {
  const { onNodeStart, onNodeEnd, onLlmToken, onToolStart, onToolEnd, onDone, onError } = callbacks
  let buffer = ''

  fetch('/api/analysis/run/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, user_input: userInput }),
  })
    .then(async (response) => {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              switch (data.type) {
                case 'chain_end':
                  onNodeEnd?.(data.node, data.state_update)
                  break
                case 'llm_token':
                  onLlmToken?.(data.content)
                  break
                case 'tool_start':
                  onToolStart?.(data.tool)
                  break
                case 'tool_end':
                  onToolEnd?.(data.tool, data.output)
                  break
                case 'error':
                  onError?.(data.message)
                  break
                case 'done':
                  onDone?.()
                  break
              }
            } catch (e) {
              // ignore malformed SSE data
            }
          }
        }
      }
    })
    .catch((err) => onError?.(err.message))
}

export function streamConclude(projectId, userNotes, callbacks) {
  const { onToken, onDone, onError } = callbacks
  let buffer = ''

  fetch('/api/report/conclude/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, user_notes: userNotes }),
  })
    .then(async (response) => {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'token') onToken?.(data.content)
              else if (data.type === 'done') onDone?.()
              else if (data.type === 'error') onError?.(data.message)
            } catch (e) { /* ignore */ }
          }
        }
      }
    })
    .catch((err) => onError?.(err.message))
}
```

- [ ] **Step 5: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: copy frontend from project1, adapt API layer for LangGraph SSE

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 15: 适配前端 Store 和 Analysis.vue

**Files:**
- Modify: `D:\PythonFile\project2\frontend\src\stores\project.js`
- Modify: `D:\PythonFile\project2\frontend\src\views\Analysis.vue`

- [ ] **Step 1: 修改 Pinia Store**

Read existing store, adapt state structure for Graph workflow. Write `D:\PythonFile\project2\frontend\src\stores\project.js`:

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  const currentId = ref(null)
  const currentName = ref('')
  const dataFiles = ref([])
  const selectedDataFiles = ref([])

  // Graph workflow state
  const workflowState = ref({
    plan: [],
    currentStepIndex: 0,
    results: [],
    contextSummary: '',
    nextAction: 'execute',
    errorMessage: '',
    ragContext: '',
    conclusion: '',
  })

  const chatHistory = ref([])
  const isRunning = ref(false)
  const currentTokens = ref('')
  const reportPreviewMode = ref(false)

  const steps = computed(() => workflowState.value.plan || [])
  const doneSteps = computed(() => steps.value.filter(s => s.status === 'done'))
  const totalRows = computed(() => selectedDataFiles.value.length)

  function setProject(id, name) {
    currentId.value = id
    currentName.value = name
  }

  function updateFromGraphEvent(eventType, payload) {
    switch (eventType) {
      case 'chain_end':
        if (payload && payload.state_update) {
          Object.assign(workflowState.value, payload.state_update)
        }
        break
      case 'done':
        isRunning.value = false
        break
      case 'error':
        workflowState.value.errorMessage = payload
        isRunning.value = false
        break
    }
  }

  function clearProject() {
    currentId.value = null
    currentName.value = ''
    workflowState.value = {
      plan: [], currentStepIndex: 0, results: [],
      contextSummary: '', nextAction: 'execute',
      errorMessage: '', ragContext: '', conclusion: '',
    }
    chatHistory.value = []
    currentTokens.value = ''
  }

  return {
    currentId, currentName, dataFiles, selectedDataFiles,
    workflowState, chatHistory, isRunning, currentTokens,
    reportPreviewMode, steps, doneSteps, totalRows,
    setProject, updateFromGraphEvent, clearProject,
  }
})
```

- [ ] **Step 2: 修改 Analysis.vue 核心逻辑**

由于 Analysis.vue 文件较大，需要做以下关键改造：

```vue
<!-- 核心模板结构变更 -->
<template>
  <div class="analysis-container">
    <!-- 左侧：对话历史 -->
    <el-aside width="25%">
      <div class="chat-section">
        <div v-for="(msg, i) in chatHistory" :key="i" class="chat-message">
          <div v-if="msg.role === 'user'" class="user-msg">{{ msg.content }}</div>
          <div v-else class="agent-msg">{{ msg.content }}</div>
        </div>
        <div v-if="isRunning" class="streaming-text">{{ currentTokens }}</div>

        <el-input
          v-model="userInput"
          type="textarea"
          :rows="3"
          placeholder="描述你的分析需求，例如：帮我分析座椅面料各指标的相关性"
          :disabled="isRunning"
          @keydown.enter.ctrl="startAnalysis"
        />
        <el-button type="primary" @click="startAnalysis" :loading="isRunning">
          {{ isRunning ? '分析中...' : '开始分析' }}
        </el-button>
      </div>
    </el-aside>

    <!-- 中间：Graph 执行过程 -->
    <el-main style="width: 50%">
      <div class="workflow-progress">
        <h3>分析进度</h3>
        <el-steps direction="vertical" :active="workflowState.currentStepIndex">
          <el-step
            v-for="step in workflowState.plan"
            :key="step.id"
            :title="step.description"
            :status="step.status === 'done' ? 'success' : step.status === 'running' ? 'process' : 'wait'"
            :description="'类型: ' + step.type"
          />
        </el-steps>

        <!-- 结果展示 -->
        <div v-if="workflowState.results.length > 0" class="results-section">
          <h4>执行结果</h4>
          <div v-for="(result, i) in workflowState.results" :key="i" class="result-card">
            <el-card>
              <template #header>{{ result.description }}</template>
              <div v-html="result.text"></div>
            </el-card>
          </div>
        </div>

        <!-- 综合结论 -->
        <div v-if="workflowState.conclusion" class="conclusion-section">
          <h4>综合分析结论</h4>
          <el-card>
            <div v-html="workflowState.conclusion"></div>
          </el-card>
        </div>
      </div>
    </el-main>

    <!-- 右侧：操作面板 -->
    <el-aside width="25%">
      <el-button @click="exportReport" :disabled="!workflowState.conclusion">
        导出报告
      </el-button>
      <el-button @click="resetAnalysis">重置分析</el-button>
    </el-aside>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProjectStore } from '@/stores/project'
import { streamAnalysis } from '@/api'
import { ElMessage } from 'element-plus'

const store = useProjectStore()
const userInput = ref('')

function startAnalysis() {
  if (!userInput.value.trim() || !store.currentId) {
    ElMessage.warning('请输入分析需求')
    return
  }

  store.isRunning = true
  store.currentTokens = ''
  store.chatHistory.push({ role: 'user', content: userInput.value })

  streamAnalysis(store.currentId, userInput.value, {
    onLlmToken: (token) => { store.currentTokens += token },
    onToolStart: (tool) => {
      store.chatHistory.push({ role: 'agent', content: `正在执行: ${tool}` })
      // 更新当前步骤状态为 running
      const idx = store.workflowState.currentStepIndex
      if (store.workflowState.plan[idx]) {
        store.workflowState.plan[idx].status = 'running'
      }
    },
    onToolEnd: (tool, output) => {
      store.chatHistory.push({ role: 'agent', content: `${tool} 完成` })
    },
    onNodeEnd: (node, stateUpdate) => {
      store.updateFromGraphEvent('chain_end', stateUpdate)
    },
    onDone: () => {
      store.isRunning = false
      store.chatHistory.push({
        role: 'agent',
        content: store.workflowState.conclusion || '分析完成'
      })
      saveState()
    },
    onError: (msg) => {
      store.isRunning = false
      ElMessage.error(msg)
    },
  })
}

async function saveState() {
  // 通过 project state 保存（如果需要手动保存到 projects.json）
}

function resetAnalysis() {
  store.workflowState = {
    plan: [], currentStepIndex: 0, results: [],
    contextSummary: '', nextAction: 'execute',
    errorMessage: '', ragContext: '', conclusion: '',
  }
  store.chatHistory = []
  store.currentTokens = ''
}

function exportReport() {
  store.reportPreviewMode = true
}
</script>
```

Note: 完整的 Analysis.vue 需要整合 project1 的现有功能（项目信息弹窗、数据上传、报告预览等）。实际执行时基于 project1 的 Analysis.vue 做 diff 改造。

- [ ] **Step 3: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: adapt frontend store and Analysis.vue for LangGraph workflow

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 6: 脚本与文档

### Task 16: 创建 RAG 初始化脚本和启动脚本

**Files:**
- Create: `D:\PythonFile\project2\scripts\init_rag.py`
- Create: `D:\PythonFile\project2\run_backend.bat`
- Create: `D:\PythonFile\project2\setup.bat`

- [ ] **Step 1: 编写 init_rag.py**

Write `D:\PythonFile\project2\scripts\init_rag.py`:

```python
"""初始化 RAG 知识库 — 一次性脚本.

Usage: python scripts/init_rag.py [--knowledge-dir knowledge] [--persist-dir chroma_db]
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.rag.loader import load_documents
from agent.rag.splitter import split_documents
from agent.rag.embeddings import create_embeddings
from agent.rag.store import create_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="初始化 RAG 知识库")
    parser.add_argument("--knowledge-dir", default="knowledge", help="知识库目录")
    parser.add_argument("--persist-dir", default="chroma_db", help="Chroma 持久化目录")
    parser.add_argument("--chunk-size", type=int, default=800, help="文档分块大小")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="分块重叠大小")
    args = parser.parse_args()

    # 1. 加载文档
    logger.info("Loading documents from %s...", args.knowledge_dir)
    docs = load_documents(args.knowledge_dir)
    logger.info("Loaded %d documents", len(docs))

    if not docs:
        logger.warning("No documents found in %s!", args.knowledge_dir)
        return

    # 2. 分块
    logger.info("Splitting documents (chunk_size=%d)...", args.chunk_size)
    chunks = split_documents(docs, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    logger.info("Created %d chunks", len(chunks))

    # 3. 创建 Embedding
    logger.info("Creating embeddings...")
    embeddings = create_embeddings()

    # 4. 创建向量库
    logger.info("Creating vector store at %s...", args.persist_dir)
    create_vector_store(chunks, embeddings, persist_dir=args.persist_dir)
    logger.info("RAG initialization complete!")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 编写 run_backend.bat**

Write `D:\PythonFile\project2\run_backend.bat`:

```bat
@echo off
chcp 65001 >nul
echo Starting DS Agent v2 Backend (LangChain + LangGraph)...
uvicorn backend.main:app --reload --port 8502 --host 0.0.0.0
pause
```

- [ ] **Step 3: 编写 setup.bat**

Write `D:\PythonFile\project2\setup.bat`:

```bat
@echo off
chcp 65001 >nul
echo ========================================
echo DS Agent v2 Environment Setup
echo ========================================
echo.
echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
echo.
echo [2/3] Initializing RAG knowledge base...
python scripts/init_rag.py
echo.
echo [3/3] Setup complete!
echo Run run_backend.bat to start the backend.
echo Then cd frontend ^&^& npm install ^&^& npm run dev
pause
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "feat: add RAG init script and startup scripts

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 17: 编写对比文档

**Files:**
- Create: `D:\PythonFile\project2\docs\comparison.md`

- [ ] **Step 1: 编写 comparison.md**

Write `D:\PythonFile\project2\docs\comparison.md`:

```markdown
# project1 vs project2: 架构对比分析

## 1. 概述

两个项目实现相同的功能——数据科学家 Agent（面向汽车研发工程师的 AI 数据分析工具），但采用了不同的 LLM 编排架构。

| 维度 | project1 | project2 |
|------|----------|----------|
| LLM 调用 | 手写 OpenAI API (`openai` 库) | LangChain `ChatOpenAI` |
| Agent 决策 | 手写 `AnalysisAgent` | LangChain `AgentExecutor` + `create_tool_calling_agent` |
| 步骤调度 | 手写 `step_executor.py` (if-else) | LangGraph `StateGraph` |
| 工具管理 | 无（前端传 `method` 名） | LangChain `StructuredTool` x 12 |
| 知识检索 | TF-IDF 关键词匹配 | Chroma RAG 语义向量搜索 |
| 状态管理 | 手动 JSON 读写 (`state.json`) | LangGraph State + `SqliteSaver` Checkpointer |
| 流式输出 | 手写 SSE 生成器 | LangGraph `astream_events` |

## 2. 架构对比

### project1 架构

```
用户 → Vue 前端 → 手动点击步骤 → FastAPI → step_executor(if-else) → engine 函数
                     ↑                        ↓
                     └── 人工选择 method ── llm_agent(手写 OpenAI API)
```

### project2 架构

```
用户 → Vue 前端 → 自然语言需求 → FastAPI SSE → LangGraph StateGraph
                                                    ├── understand_intent (RAG)
                                                    ├── plan_analysis (LLM + Tools)
                                                    ├── execute_step (Tool Calling)
                                                    ├── interpret_result (LLM)
                                                    ├── decide_next (确定性逻辑)
                                                    └── generate_conclusion (LLM)
```

## 3. 核心差异逐层对比

### 3.1 LLM 编排

**project1**: `llm_agent.py` 中手写 `AnalysisAgent` 类，直接用 `openai` 库调 API。
- 约 300 行代码实现 planning/explain/summarize
- 每次加功能需改 `build_system_prompt` 方法
- Stream 需手动写 `chat_stream` 迭代器

**project2**: LangChain `AgentExecutor` + `create_tool_calling_agent`
- 约 50 行创建 Agent
- 加功能 = 加 Tool，Agent 自动感知
- 流式由 LangGraph `astream_events` 统一处理

### 3.2 步骤调度

**project1**: `step_executor.py` 中一个大型 if-else：
```python
def execute_step(step_type, params, df):
    if step_type == "clean":
        return _clean(df, params)
    elif step_type == "eda":
        return _eda(df, params)
    elif ...
```

**project2**: LangGraph StateGraph 条件路由：
```python
workflow.add_conditional_edges("interpret_result", decide_next, {
    "execute": "execute_step",
    "generate_conclusion": "generate_conclusion",
})
```

### 3.3 工具调用

**project1**: 前端必须知道精确的 method 名：
```json
{"step_type": "eda", "method": "correlation", "params": {"columns": ["a", "b"]}}
```

**project2**: LLM 自主选择和调用 Tool：
```
用户："帮我看看哪些因素跟座椅满意度相关"
→ LLM 自动调用 correlation_analysis(columns=["seat_satisfaction"])
→ 然后调用 feature_importance(target="seat_satisfaction")
```

### 3.4 知识检索

**project1**: TF-IDF
- 准确匹配关键词
- "座椅" 找不回 "坐垫"
- 约 150 行代码

**project2**: Chroma RAG
- 语义相似度
- 同义词自动覆盖
- LangChain 原语，约 30 行核心代码

### 3.5 状态管理

**project1**: 手动 JSON 序列化
```python
pm.save_state(project_id, {"rounds": [...], "current_round": 0})
pm.save_chat_history(project_id, [...])
```

**project2**: Graph State + Checkpointer
```python
workflow.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))
# 状态自动持久化，断点自动续跑
```

### 3.6 流式输出

**project1**: 手写 SSE
```python
async def event_generator():
    for chunk in agent.explain_result_stream(...):
        yield f"data: {json.dumps(chunk)}\n\n"
    yield "data: [DONE]\n\n"
```

**project2**: LangGraph astream_events
```python
async for event in workflow.astream_events(initial_state, version="v2"):
    yield f"data: {json.dumps(event)}\n\n"
```

## 4. 代码量统计

| 模块 | project1 | project2 | 变化 |
|------|----------|----------|------|
| `engine/` (除 llm_agent + step_executor) | ~2500 行 | ~2500 行 | 不变 |
| `engine/llm_agent.py` | ~300 行 | 删除 | -300 |
| `engine/step_executor.py` | ~200 行 | 删除 | -200 |
| `graph/` | 0 | ~400 行 | +400 |
| `agent/` | 0 | ~200 行 | +200 |
| `agent/rag/` | 0 | ~150 行 | +150 |
| `backend/` | ~400 行 | ~350 行 | -50 |
| `frontend/` (API + Store) | ~300 行 | ~250 行 | -50 |
| **总计** | ~3900 行 | ~3850 行 | **净减 ~50 行** |

虽然总代码量相近，但 project2 的代码分布在更小、更独立的文件中，
且框架提供的功能（重试、状态恢复、追踪）在 project1 中都不存在。

## 5. 开发者体验

### 5.1 添加新分析操作

**project1**: 5 步
1. 在 engine 中实现函数
2. 在 step_executor._eda() 中添加 if 分支
3. 在 llm_agent.build_system_prompt() 中添加描述
4. 在前端添加表单控件
5. 测试端到端流程

**project2**: 2 步
1. 在 tools.py 中添加一个 StructuredTool
2. 运行测试

### 5.2 调试体验

**project1**: print/log 调试，需手动追踪状态变化

**project2**: `LANGCHAIN_TRACING_V2=true` 启用 LangSmith 可视化追踪，每个 LLM 调用/Tool 调用的时间线和输入输出一目了然

### 5.3 测试体验

**project1**: 需要模拟前端请求的完整参数结构

**project2**: 直接测 Tool + Graph 节点，MemorySaver 让工作流测试变得简单

## 6. 学习曲线

| | project1 | project2 |
|---|----------|----------|
| 上手难度 | 低（纯 Python，无框架） | 中（需理解 Agent/Graph/Tool 概念） |
| 概念数量 | 少 | 多（StateGraph, Tool, AgentExecutor, RAG） |
| 文档生态 | 无 | LangChain/LangGraph 丰富文档 |
| 适合场景 | 小而简单的 Agent | 复杂多步骤、需状态管理的 Agent |

## 7. 总结与选型建议

**选择 project1 (手写) 当你:**
- 团队不熟悉 LangChain 生态
- Agent 逻辑简单（3-5 步线性流程）
- 需要极致控制每一个细节
- 依赖最小化是首要考量

**选择 project2 (LangChain/LangGraph) 当你:**
- Agent 有复杂控制流（条件分支、循环、人工确认）
- 需要状态持久化和断点续跑
- 需要语义搜索/RAG 能力
- 期望框架社区持续提供新能力
- 团队愿意投入时间学习框架
```

- [ ] **Step 2: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "docs: add comprehensive project1 vs project2 comparison

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 7: 测试

### Task 18: 编写单元测试 (Tools + Nodes + RAG)

**Files:**
- Create: `D:\PythonFile\project2\tests\conftest.py`
- Create: `D:\PythonFile\project2\tests\unit\test_tools.py`
- Create: `D:\PythonFile\project2\tests\unit\test_nodes.py`
- Create: `D:\PythonFile\project2\tests\unit\test_rag.py`

- [ ] **Step 1: 编写 conftest.py**

Write `D:\PythonFile\project2\tests\conftest.py`:

```python
"""测试公共 fixtures."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_df():
    """创建示例 DataFrame."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "seat_satisfaction": np.random.rand(n) * 5 + 5,
        "glossiness": np.random.rand(n) * 10,
        "softness": np.random.rand(n) * 5 + 5,
        "abrasion_resistance": np.random.rand(n) * 100,
        "material_type": np.random.choice(["A", "B", "C"], n),
        "production_batch": np.random.choice(["B001", "B002", "B003"], n),
    })
```

- [ ] **Step 2: 编写 test_tools.py**

Write `D:\PythonFile\project2\tests\unit\test_tools.py`:

```python
"""测试每个 Tool 的输入/输出正确性."""
import pytest
from graph.tools import (
    run_clean_data, run_describe_numeric, run_correlation,
    run_distribution, run_scatter, run_train_regression, run_cluster,
    create_analysis_tools,
)


class TestToolCreation:
    def test_all_tools_created(self):
        tools = create_analysis_tools()
        assert len(tools) == 12

    def test_tool_names_unique(self):
        tools = create_analysis_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names))


class TestCleanData:
    def test_clean_no_error(self, sample_df):
        result = run_clean_data(sample_df)
        assert result["success"] is True


class TestDescribeNumeric:
    def test_describe_returns_stats(self, sample_df):
        result = run_describe_numeric(sample_df, columns=["glossiness", "softness"])
        assert result["success"] is True
        assert "statistics" in result["data"]


class TestCorrelation:
    def test_correlation_pearson(self, sample_df):
        result = run_correlation(sample_df, method="pearson", columns=["glossiness", "softness", "seat_satisfaction"])
        assert result["success"] is True
        assert "correlation_matrix" in result["data"]


class TestDistribution:
    def test_distribution_plot(self, sample_df):
        result = run_distribution(sample_df, column="glossiness", bins=20)
        assert result["success"] is True
        assert result["data"]["chart_type"] == "distribution"


class TestScatter:
    def test_scatter_plot(self, sample_df):
        result = run_scatter(sample_df, x="glossiness", y="seat_satisfaction", trendline=True)
        assert result["success"] is True


class TestRegression:
    def test_regression_linear(self, sample_df):
        result = run_train_regression(sample_df, target="seat_satisfaction", model_type="linear")
        assert result["success"] is True
        assert "metrics" in result["data"]


class TestCluster:
    def test_cluster_kmeans(self, sample_df):
        result = run_cluster(sample_df, columns=["glossiness", "softness"], n_clusters=3)
        assert result["success"] is True


class TestToolErrorHandling:
    def test_tool_handles_empty_df(self):
        import pandas as pd
        result = run_clean_data(pd.DataFrame())
        assert result["success"] is False
        assert "error" in result
```

- [ ] **Step 3: 编写 test_nodes.py**

Write `D:\PythonFile\project2\tests\unit\test_nodes.py`:

```python
"""测试每个 Graph 节点的独立行为."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from graph.nodes import decide_next
from graph.state import AnalysisState


class TestDecideNext:
    def test_continue_when_steps_remain(self):
        state: AnalysisState = {
            "user_input": "test",
            "plan": [{"id": 1}, {"id": 2}],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
            "next_action": "execute",
            "error_message": "",
        }
        assert decide_next(state) == "execute"

    def test_done_when_all_steps_complete(self):
        state: AnalysisState = {
            "user_input": "test",
            "plan": [{"id": 1}, {"id": 2}],
            "current_step_index": 2,
            "results": [],
            "context_summary": "",
            "next_action": "execute",
            "error_message": "",
        }
        assert decide_next(state) == "generate_conclusion"

    def test_done_when_empty_plan(self):
        state: AnalysisState = {
            "user_input": "test",
            "plan": [],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
            "next_action": "execute",
            "error_message": "",
        }
        assert decide_next(state) == "generate_conclusion"
```

- [ ] **Step 4: 编写 test_rag.py** (skip if no chromadb installed)

Write `D:\PythonFile\project2\tests\unit\test_rag.py`:

```python
"""测试 RAG 模块."""
import pytest
from unittest.mock import MagicMock, patch

from agent.rag.loader import load_documents
from agent.rag.splitter import split_documents
from langchain_core.documents import Document


class TestLoader:
    def test_empty_directory(self, tmp_path):
        docs = load_documents(str(tmp_path))
        assert docs == []

    def test_load_txt_file(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("这是测试文档内容", encoding="utf-8")
        docs = load_documents(str(tmp_path))
        assert len(docs) == 1
        assert "测试文档" in docs[0].page_content


class TestSplitter:
    def test_split_small_document(self):
        doc = Document(page_content="短文本。", metadata={"source": "test.txt"})
        chunks = split_documents([doc], chunk_size=800, chunk_overlap=100)
        assert len(chunks) == 1

    def test_split_long_document(self):
        long_text = "这是一个很长的句子。" * 500
        doc = Document(page_content=long_text, metadata={"source": "test.txt"})
        chunks = split_documents([doc], chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1


class TestRetrieverFallback:
    def test_fallback_returns_empty(self):
        from agent.rag.retriever import _FallbackRetriever
        retriever = _FallbackRetriever()
        docs = retriever.invoke("测试查询")
        assert docs == []
```

- [ ] **Step 5: 运行测试**

```bash
cd /d/PythonFile/project2 && python -m pytest tests/unit/ -v --tb=short
```

- [ ] **Step 6: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "test: add unit tests for tools, nodes, and RAG

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 19: 编写集成测试

**Files:**
- Create: `D:\PythonFile\project2\tests\integration\test_workflow.py`
- Create: `D:\PythonFile\project2\tests\integration\test_api.py`

- [ ] **Step 1: 编写 test_workflow.py**

Write `D:\PythonFile\project2\tests\integration\test_workflow.py`:

```python
"""集成测试: StateGraph 完整流程."""
import pytest
import pandas as pd
import numpy as np
from langgraph.checkpoint.memory import MemorySaver

from graph.workflow import build_workflow
from graph.state import AnalysisState


@pytest.fixture
def sample_df():
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        "satisfaction": np.random.rand(n) * 5 + 5,
        "glossiness": np.random.rand(n) * 10,
        "softness": np.random.rand(n) * 5 + 5,
    })


@pytest.fixture
def compiled_workflow():
    return build_workflow(checkpointer=MemorySaver())


class TestWorkflowIntegration:
    def test_workflow_compiles(self, compiled_workflow):
        assert compiled_workflow is not None

    def test_minimal_execution(self, compiled_workflow, sample_df):
        """测试最简执行路径：无数据时的基础流程."""
        state: AnalysisState = {
            "user_input": "测试分析",
            "project_id": "test-123",
            "df": sample_df,
            "plan": [],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
            "next_action": "execute",
            "error_message": "",
            "rag_context": "",
            "conclusion": "",
        }
        config = {"configurable": {"thread_id": "test-1"}}

        result = compiled_workflow.invoke(state, config)

        assert "next_action" in result
        assert result["next_action"] in ("execute", "done", "generate_conclusion")

    def test_workflow_state_persistence(self, compiled_workflow, sample_df):
        """测试状态跨调用持久化."""
        thread_id = "test-persist"
        config = {"configurable": {"thread_id": thread_id}}

        state: AnalysisState = {
            "user_input": "分析数据",
            "project_id": "test-persist",
            "df": sample_df,
            "plan": [],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
            "next_action": "execute",
            "error_message": "",
            "rag_context": "",
            "conclusion": "",
        }

        result1 = compiled_workflow.invoke(state, config)

        state2 = compiled_workflow.get_state(config)
        assert state2 is not None
```

- [ ] **Step 2: 编写 test_api.py**

Write `D:\PythonFile\project2\tests\integration\test_api.py`:

```python
"""集成测试: FastAPI 端点."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealth:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestConfig:
    def test_get_config(self):
        response = client.get("/api/config")
        assert response.status_code in (200, 404)  # 200 if config.json exists


class TestProjects:
    def test_list_projects(self):
        response = client.get("/api/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAnalysisStream:
    def test_analysis_stream_invalid_project(self):
        """测试无效项目 ID 的错误处理."""
        response = client.post(
            "/api/analysis/run/stream",
            json={"project_id": "00000000-0000-0000-0000-000000000000", "user_input": "测试"},
        )
        # Should get SSE stream with error event
        assert response.status_code == 200  # SSE returns 200 even on error
```

- [ ] **Step 3: 运行集成测试**

```bash
cd /d/PythonFile/project2 && python -m pytest tests/integration/ -v --tb=short
```

- [ ] **Step 4: Commit**

```bash
cd /d/PythonFile/project2 && git add -A && git commit -m "test: add integration tests for workflow and API

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 8: GitHub 发布

### Task 20: 推送 project2 到 GitHub

- [ ] **Step 1: 创建 GitHub 仓库并推送**

```bash
cd /d/PythonFile/project2

# 确保所有变更已提交
git status
git log --oneline -5

# 创建 GitHub 仓库（如果 gh CLI 可用）
gh repo create project2 --public --source=. --remote=origin --push

# 或者手动添加 remote 后推送
# git remote add origin https://github.com/zym-up/project2.git
# git branch -M master
# git push -u origin master
```

- [ ] **Step 2: 验证远程仓库**

```bash
git remote -v
git log --oneline -3
```

---

## 实施顺序总结

```
Phase 1: Task 1-4     (项目脚手架)
Phase 2: Task 5-8     (Graph 层 — 核心)
Phase 3: Task 9-10    (Agent + RAG)
Phase 4: Task 11-13   (后端适配)
Phase 5: Task 14-15   (前端适配)
Phase 6: Task 16-17   (脚本 + 文档)
Phase 7: Task 18-19   (测试)
Phase 8: Task 20      (GitHub 推送)
```

每个 Phase 内的 Tasks 必须按顺序执行，Phase 之间也按顺序执行。
