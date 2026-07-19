"""LangChain Agent manager — create and configure analysis Agent."""
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
    """Create analysis Agent.

    Args:
        base_url: API base URL
        api_key: API key
        model: Model name
        temperature: Temperature parameter
        max_tokens: Max tokens

    Returns:
        Configured AgentExecutor instance
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
