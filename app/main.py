"""
FastAPI 应用入口 — 提供 POST /chat 和 GET /health 接口。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import ChatRequest, ChatResponse
from .agent import run_agent

# ── 应用初始化 ────────────────────────────────────────────────
app = FastAPI(
    title="AI Agent Backend",
    description="FastAPI + LangChain + DeepSeek 驱动的智能 Agent 服务，集成天气查询与计算器工具。",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 端点 ──────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """健康检查端点，供 Kubernetes / Docker Compose 探活使用。"""
    return {"status": "ok", "service": "ai-agent-backend", "version": "1.0.0"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """接收用户 prompt，交给 Agent 处理并返回最终回答。

    Agent 会自动判断是否需要调用工具（天气查询 / 计算器），
    必要时可多次调用工具直到得出最终结论。

    支持多轮对话：传入相同的 thread_id 可延续之前的对话上下文。

    示例请求体：
    ```json
    {"prompt": "北京今天天气怎么样？", "thread_id": "session-001"}
    ```
    """
    answer = await run_agent(req.prompt, thread_id=req.thread_id)
    return ChatResponse(answer=answer)


# ── 本地开发入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    from .config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
