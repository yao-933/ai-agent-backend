"""
Pydantic 数据模型 — 请求 / 响应的结构定义。
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="用户发给 AI Agent 的提示词",
        examples=["北京今天天气怎么样？", "计算 (123 + 456) * 7 / 3"],
        min_length=1,
        max_length=4096,
    )
    thread_id: str = Field(
        default="default",
        description="会话标识符。同一 thread_id 共享对话历史，实现多轮记忆。",
        examples=["default", "session-001", "user-42"],
        max_length=128,
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Agent 的最终回答（仅包含最终回复文本）")
