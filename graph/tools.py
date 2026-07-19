"""LangChain Tool — analysis operations as StructuredTools.

Tool layer wraps engine functions — no business logic here.
LLM selects tools autonomously via Function Calling.
"""
import json
import time
import traceback
from functools import wraps
from typing import Optional

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import pandas as pd

from engine import data_cleaner, eda, feature_engineer, modeler


# === Pydantic input schemas ===

class CleanInput(BaseModel):
    drop_dup: bool = Field(True, description="remove duplicates")
    fill_strategy: str = Field("mean", description="fill strategy: mean/median/mode/constant")
    outlier_method: str = Field("iqr", description="outlier detection: iqr/zscore")


class FillMissingInput(BaseModel):
    strategy: str = Field("mean", description="fill strategy")
    columns: Optional[list[str]] = Field(None, description="column names to fill")
    fill_value: Optional[float] = Field(None, description="value when strategy=constant")


class DescribeNumericInput(BaseModel):
    columns: Optional[list[str]] = Field(None, description="numeric columns to describe")


class CorrelationInput(BaseModel):
    method: str = Field("pearson", description="correlation method: pearson/spearman")
    columns: Optional[list[str]] = Field(None, description="columns to analyze")


class DistributionInput(BaseModel):
    column: str = Field(..., description="column name to plot")
    bins: int = Field(30, description="histogram bins")


class ScatterInput(BaseModel):
    x: str = Field(..., description="x-axis column")
    y: str = Field(..., description="y-axis column")
    color: Optional[str] = Field(None, description="group color column")
    trendline: bool = Field(True, description="add trendline")


class LineInput(BaseModel):
    x: str = Field(..., description="x-axis column")
    y: str = Field(..., description="y-axis column")
    group_by: Optional[str] = Field(None, description="group by column")


class ScaleInput(BaseModel):
    columns: list[str] = Field(..., description="columns to scale")
    method: str = Field("standard", description="scale method: standard/minmax")


class EncodeInput(BaseModel):
    columns: list[str] = Field(..., description="columns to encode")
    method: str = Field("onehot", description="encode method: onehot/label")


class TrainRegressionInput(BaseModel):
    target: str = Field(..., description="target column name")
    model_type: str = Field("linear", description="model: linear/ridge/lasso/random_forest/xgboost")
    test_size: float = Field(0.2, description="test set ratio")
    feature_columns: Optional[list[str]] = Field(None, description="feature columns")


class ClusterInput(BaseModel):
    columns: list[str] = Field(..., description="cluster feature columns")
    n_clusters: int = Field(3, description="number of clusters")


class FeatureImportanceInput(BaseModel):
    target: str = Field(..., description="target column")
    feature_columns: Optional[list[str]] = Field(None, description="feature columns")


# === Tool execution functions ===

def _safe_tool(func):
    """Wrap tool with error handling and unified result format."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = round((time.time() - start) * 1000)
            return {"success": True, "data": result, "elapsed_ms": elapsed}
        except Exception as e:
            elapsed = round((time.time() - start) * 1000)
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "elapsed_ms": elapsed,
            }
    return wrapper


def _to_json_safe(obj):
    """Convert result to JSON-safe dict."""
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_json_safe(v) for v in obj]
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj


@_safe_tool
def run_clean_data(df: pd.DataFrame, drop_dup: bool = True,
                   fill_strategy: str = "mean", outlier_method: str = "iqr") -> dict:
    cleaned_df, summary = data_cleaner.clean_pipeline(
        df, drop_dup=drop_dup, fill_strategy=fill_strategy, outlier_method=outlier_method
    )
    return {"summary": _to_json_safe(summary), "row_count": len(cleaned_df), "col_count": len(cleaned_df.columns)}


@_safe_tool
def run_fill_missing(df: pd.DataFrame, strategy: str = "mean",
                     columns: Optional[list] = None, fill_value=None) -> dict:
    _, summary = data_cleaner.fill_missing(df, strategy=strategy, columns=columns, fill_value=fill_value)
    return {"summary": _to_json_safe(summary)}


@_safe_tool
def run_describe_numeric(df: pd.DataFrame, columns: Optional[list] = None) -> dict:
    result = eda.describe_numeric(df, columns=columns)
    return {"statistics": _to_json_safe(result)}


@_safe_tool
def run_correlation(df: pd.DataFrame, method: str = "pearson",
                    columns: Optional[list] = None) -> dict:
    corr_df, _ = eda.correlation_matrix(df, method=method, columns=columns)
    return {"correlation_matrix": corr_df.to_dict()}


@_safe_tool
def run_distribution(df: pd.DataFrame, column: str, bins: int = 30) -> dict:
    eda.distribution_plot(df, column=column, bins=bins)
    return {"chart_type": "distribution", "column": column}


@_safe_tool
def run_scatter(df: pd.DataFrame, x: str, y: str,
                color: Optional[str] = None, trendline: bool = True) -> dict:
    eda.scatter_plot(df, x=x, y=y, color=color, trendline=trendline)
    return {"chart_type": "scatter", "x": x, "y": y}


@_safe_tool
def run_line(df: pd.DataFrame, x: str, y: str, group_by: Optional[str] = None) -> dict:
    eda.line_plot(df, x=x, y=y, group_by=group_by)
    return {"chart_type": "line", "x": x, "y": y}


@_safe_tool
def run_scale_features(df: pd.DataFrame, columns: list, method: str = "standard") -> dict:
    scaled_df, summary = feature_engineer.scale_features(df, columns, method=method)
    return {"summary": _to_json_safe(summary), "columns_scaled": len(columns)}


@_safe_tool
def run_encode(df: pd.DataFrame, columns: list, method: str = "onehot") -> dict:
    encoded_df, summary = feature_engineer.encode_categorical(df, columns, method=method)
    return {"summary": _to_json_safe(summary), "columns_encoded": len(columns)}


@_safe_tool
def run_train_regression(df: pd.DataFrame, target: str, model_type: str = "linear",
                         test_size: float = 0.2, feature_columns: Optional[list] = None) -> dict:
    if feature_columns:
        X = df[feature_columns]
    else:
        X = df.select_dtypes(include=["number"]).drop(columns=[target], errors="ignore")
    y = df[target]
    X_train, X_test, y_train, y_test = modeler.split_data(X, y, target=target, test_size=test_size)
    model_obj, train_summary = modeler.train_regression(X_train, y_train, model_type=model_type)
    eval_metrics = modeler.evaluate_regression(model_obj, X_test, y_test)
    return {"train_summary": _to_json_safe(train_summary), "metrics": _to_json_safe(eval_metrics)}


@_safe_tool
def run_cluster(df: pd.DataFrame, columns: list, n_clusters: int = 3) -> dict:
    result_df, summary, fig = modeler.train_cluster(df, columns=columns, n_clusters=n_clusters)
    return {"summary": _to_json_safe(summary), "cluster_count": n_clusters}


@_safe_tool
def run_feature_importance(df: pd.DataFrame, target: str,
                           feature_columns: Optional[list] = None) -> dict:
    if feature_columns:
        X = df[feature_columns]
    else:
        X = df.select_dtypes(include=["number"]).drop(columns=[target], errors="ignore")
    y = df[target]
    X_train, X_test, y_train, y_test = modeler.split_data(X, y, target=target)
    model_obj, _ = modeler.train_regression(X_train, y_train, model_type="random_forest")
    imp_df, _ = modeler.feature_importance(model_obj, X.columns.tolist())
    return {"feature_importance": imp_df.to_dict()}


# === Build tool list ===

def create_analysis_tools() -> list[StructuredTool]:
    """Create all analysis tools for Agent use."""
    return [
        StructuredTool.from_function(
            name="clean_data",
            description="Clean data: remove duplicates, fill missing values (mean/median/mode), detect outliers (IQR/Z-score). Usually the first analysis step.",
            args_schema=CleanInput,
            func=run_clean_data,
        ),
        StructuredTool.from_function(
            name="fill_missing_values",
            description="Fill missing values using mean/median/mode/constant strategy",
            args_schema=FillMissingInput,
            func=run_fill_missing,
        ),
        StructuredTool.from_function(
            name="describe_numeric",
            description="Descriptive statistics for numeric columns: mean, std, quartiles, skewness, kurtosis.",
            args_schema=DescribeNumericInput,
            func=run_describe_numeric,
        ),
        StructuredTool.from_function(
            name="correlation_analysis",
            description="Compute correlation matrix (Pearson/Spearman) to find linear relationships between variables.",
            args_schema=CorrelationInput,
            func=run_correlation,
        ),
        StructuredTool.from_function(
            name="distribution_plot",
            description="Generate distribution plot (histogram + boxplot) for a single variable.",
            args_schema=DistributionInput,
            func=run_distribution,
        ),
        StructuredTool.from_function(
            name="scatter_plot",
            description="Generate scatter plot with optional trendline and color grouping.",
            args_schema=ScatterInput,
            func=run_scatter,
        ),
        StructuredTool.from_function(
            name="line_plot",
            description="Generate line plot, optionally grouped by a column.",
            args_schema=LineInput,
            func=run_line,
        ),
        StructuredTool.from_function(
            name="scale_features",
            description="Feature scaling: Z-score standardization or Min-Max normalization. Required before modeling.",
            args_schema=ScaleInput,
            func=run_scale_features,
        ),
        StructuredTool.from_function(
            name="encode_categorical",
            description="Encode categorical variables: one-hot encoding or label encoding.",
            args_schema=EncodeInput,
            func=run_encode,
        ),
        StructuredTool.from_function(
            name="train_regression",
            description="Train regression model (linear/ridge/lasso/random_forest/xgboost). Returns R2/MSE/MAE.",
            args_schema=TrainRegressionInput,
            func=run_train_regression,
        ),
        StructuredTool.from_function(
            name="cluster_analysis",
            description="K-Means clustering to discover natural groupings in data.",
            args_schema=ClusterInput,
            func=run_cluster,
        ),
        StructuredTool.from_function(
            name="feature_importance",
            description="Analyze feature importance using Random Forest. Ranks features by impact on target variable.",
            args_schema=FeatureImportanceInput,
            func=run_feature_importance,
        ),
    ]
