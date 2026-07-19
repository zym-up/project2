"""Pydantic request/response models."""
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
    """Unified streaming analysis request."""
    project_id: str = Field(..., pattern=r'^[a-f0-9-]{36}$')
    user_input: str = Field(..., min_length=1, max_length=5000)

    @field_validator("user_input")
    @classmethod
    def sanitize(cls, v: str) -> str:
        cleaned = re.sub(r'[<>{}]', '', v)
        if len(cleaned.strip()) < 1:
            raise ValueError("Input cannot be empty")
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
