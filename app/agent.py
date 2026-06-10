"""
LangChain v1 Agent — 使用 create_agent + InMemorySaver。

核心特性：
- create_agent（langchain.agents）：v1 推荐 API，替代废弃的 create_react_agent
- InMemorySaver（langgraph.checkpoint）：会话级记忆持久化
- system_prompt：控制 Agent 行为风格
- 多轮对话：同一 thread_id 共享历史上下文
"""

import httpx
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI

from .config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME
from .tools import ALL_TOOLS

# ══════════════════════════════════════════════════════════════════
# HTTP 客户端（Windows 兼容 SSL）
# ══════════════════════════════════════════════════════════════════
# Windows 下 Python 常因系统证书缺失导致 SSL 验证失败。
# 生产环境请配置好系统证书后把 verify=False 改为 verify=True。
_verify = False

_http_client = httpx.Client(
    verify=_verify,
    timeout=httpx.Timeout(60.0),
)
_async_http_client = httpx.AsyncClient(
    verify=_verify,
    timeout=httpx.Timeout(60.0),
)

# ══════════════════════════════════════════════════════════════════
# LLM 实例
# ══════════════════════════════════════════════════════════════════
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=MODEL_NAME,
    temperature=0,          # Agent 任务建议 0，确保稳定可预测
    max_tokens=2048,
    http_client=_http_client,
    http_async_client=_async_http_client,
)

# ══════════════════════════════════════════════════════════════════
# System Prompt
# ══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """\
You are a helpful AI assistant with access to real-time tools.

## Available Tools
- **get_weather**: Query the current weather for any supported city.
- **calculator**: Evaluate a mathematical expression safely.

## Instructions
1. Use tools whenever they help answer the user's question accurately.
2. Respond in the **same language** the user uses (中文问题用中文回答, English questions in English).
3. Keep answers **concise and clear** — no unnecessary explanation unless asked.
4. When the user references previous conversation context, use memory to stay coherent.
5. If a tool returns an error, explain it to the user gracefully.
"""

# ══════════════════════════════════════════════════════════════════
# 记忆 & Agent 构建
# ══════════════════════════════════════════════════════════════════
# InMemorySaver — 按 thread_id 隔离会话历史，同一 ID 共享上下文
# 开发/测试用；生产环境换 SqliteSaver 或 PostgresSaver
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)

# ══════════════════════════════════════════════════════════════════
# 公开接口
# ══════════════════════════════════════════════════════════════════

async def run_agent(prompt: str, thread_id: str = "default") -> str:
    """异步运行 Agent，支持多轮对话记忆。

    Args:
        prompt: 用户输入的自然语言指令。
        thread_id: 会话标识符。同一 thread_id 共享对话历史，
                   不同 thread_id 完全隔离。默认 "default"。

    Returns:
        Agent 最终回复文本。
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
    )
    # 遍历消息列表，取最后一条 AI 消息作为最终回答
    messages = result["messages"]
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and msg.type == "ai":
            return msg.content
    return "Agent 未能生成回答，请重试。"
