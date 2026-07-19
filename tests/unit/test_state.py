import pytest
from graph.state import AnalysisState


class TestAnalysisState:
    def test_state_defaults(self):
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

    def test_results_accumulate(self):
        state: AnalysisState = {
            "user_input": "test",
            "plan": [],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
            "next_action": "done",
        }
        result: dict = {"step_id": 1, "type": "eda", "status": "done", "text": "ok"}
        state["results"].append(result)
        assert len(state["results"]) == 1
        assert state["results"][0]["status"] == "done"

    def test_df_is_optional(self):
        state: AnalysisState = {
            "user_input": "no df",
            "plan": [],
            "current_step_index": 0,
            "results": [],
            "context_summary": "",
        }
        assert state.get("df") is None
