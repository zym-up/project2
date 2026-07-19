"""Test each tool's input/output correctness."""
import pytest
from graph.tools import (
    run_clean_data, run_describe_numeric, run_correlation,
    run_distribution, run_scatter, run_train_regression, run_cluster,
    create_analysis_tools,
)


class TestToolCreation:
    def test_all_12_tools(self):
        tools = create_analysis_tools()
        assert len(tools) == 12

    def test_tool_names_unique(self):
        tools = create_analysis_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names))


class TestCleanData:
    def test_clean_succeeds(self, sample_df):
        result = run_clean_data(sample_df)
        assert result["success"] is True


class TestDescribeNumeric:
    def test_describe_returns_stats(self, sample_df):
        result = run_describe_numeric(sample_df, columns=["glossiness", "softness"])
        assert result["success"] is True
        assert "statistics" in result["data"]


class TestCorrelation:
    def test_correlation_pearson(self, sample_df):
        result = run_correlation(sample_df, method="pearson",
                                 columns=["glossiness", "softness", "seat_satisfaction"])
        assert result["success"] is True


class TestDistribution:
    def test_distribution_plot(self, sample_df):
        result = run_distribution(sample_df, column="glossiness", bins=20)
        assert result["success"] is True


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


class TestErrorHandling:
    def test_tool_handles_empty_df(self):
        import pandas as pd
        result = run_clean_data(pd.DataFrame())
        assert result["success"] is False
        assert "error" in result
