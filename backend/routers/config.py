"""Config and health check routes."""
from fastapi import APIRouter
from engine.config import load_config, save_config, LLMConfig, AppConfig
from backend.models.schemas import LLMConfigSchema

router = APIRouter(prefix="/api", tags=["config"])


def _test_llm_connection(schema: LLMConfigSchema) -> tuple[bool, str]:
    """Test LLM API connection using langchain_openai."""
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            base_url=schema.base_url,
            api_key=schema.api_key,
            model=schema.model,
            max_tokens=10,
            timeout=15,
            max_retries=1,
        )
        llm.invoke("ping")
        return True, "连接成功"
    except Exception as e:
        return False, str(e)


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
    ok, msg = _test_llm_connection(schema)
    return {"success": ok, "message": msg}
