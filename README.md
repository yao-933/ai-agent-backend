# 🤖 AI Agent Backend

**FastAPI + LangChain v1 + LangGraph + DeepSeek** 驱动的智能 Agent 后端服务。

内置 **天气查询** 和 **简单计算器** 两个工具，Agent 会根据用户意图自动判断是否调用工具，支持多轮工具调用与推理链。

### ✨ 核心功能

- 🤖 **Agent 自动推理** — 基于 `create_agent`（LangChain v1 最新 API）构建
- 🧠 **多轮对话记忆** — 同一 `thread_id` 共享会话历史，支持连续追问
- 💾 **状态持久化** — `InMemorySaver` 自动保存/恢复对话状态（可升级为 SQLite / Postgres）
- 🔧 **工具调用** — 内置天气查询 + 计算器，轻松扩展新工具
- 🌐 **OpenAI 兼容** — 默认 DeepSeek，一行配置切 OpenAI / vLLM / OneAPI

---

## 📁 项目结构

```
ai-agent-backend/
├── app/
│   ├── __init__.py      # 包标记
│   ├── config.py        # 环境变量 / 配置中心
│   ├── models.py        # Pydantic 请求 / 响应模型
│   ├── tools.py         # 工具定义（天气 + 计算器）
│   ├── agent.py         # create_agent + InMemorySaver 核心
│   └── main.py          # FastAPI 应用入口（/chat, /health）
├── batch_process.py     # CSV 批量处理脚本
├── requirements.txt     # Python 依赖
├── Dockerfile           # 容器镜像
├── docker-compose.yaml  # Docker Compose 编排
├── .env.example         # 环境变量模板
├── .gitignore
├── input.csv            # 示例输入
└── README.md            # 本文件
```

---

## 🚀 快速开始

### 1. 克隆 & 安装

```bash
cd ai-agent-backend

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key：

```env
OPENAI_API_KEY=sk-your-real-api-key
OPENAI_BASE_URL=https://api.deepseek.com   # DeepSeek 官方
MODEL_NAME=deepseek-chat
```

> **💡 使用 OpenAI 官方？**
> 把 `OPENAI_BASE_URL` 改成 `https://api.openai.com/v1`，`MODEL_NAME` 改成 `gpt-4o` 即可。任何兼容 OpenAI 接口的服务（OneAPI、vLLM、LocalAI 等）都可以直接使用。

### 3. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看 Swagger 文档。

### 4. 测试 API

```bash
# 天气
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "北京今天天气怎么样？"}'

# 计算器
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "计算 (135 + 267) × 14 ÷ 6"}'

# 复合任务（Agent 自动调用多个工具）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "北京和上海哪个更热？温差是多少？"}'

# 多轮对话记忆（同一个 thread_id 保持上下文）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "帮我算 100 除以 4", "thread_id": "my-session"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "把刚才的结果乘以 6", "thread_id": "my-session"}'
```

---

## 📊 批量处理

```bash
# 直接模式（推荐，更快）
python batch_process.py --input input.csv --output output.csv

# HTTP 模式（先启动服务，再运行）
python batch_process.py --mode http --url http://localhost:8000
```

`input.csv` 格式要求至少包含一列 `prompt`：

```csv
prompt
北京今天天气怎么样？
计算 2 的 20 次方
```

输出 `output.csv` 包含两列：`prompt` 和 `answer`。

---

## 🐳 Docker 部署

```bash
# 构建并启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

---

## 🔧 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | — | API 密钥（DeepSeek / OpenAI） |
| `OPENAI_BASE_URL` | ❌ | `https://api.deepseek.com` | API 地址，可替换为任意 OpenAI 兼容服务 |
| `MODEL_NAME` | ❌ | `deepseek-chat` | 模型名称（如 `gpt-4o`、`gpt-4o-mini`） |
| `HOST` | ❌ | `0.0.0.0` | 服务监听地址 |
| `PORT` | ❌ | `8000` | 服务监听端口 |

---

## 🛠️ 已有工具

| 工具 | 说明 |
|---|---|
| `get_weather` | 查询城市天气（当前为模拟数据，可替换为真实 API） |
| `calculator` | 安全数学表达式求值（仅允许数字与运算符，防注入） |

### 添加新工具

在 [app/tools.py](app/tools.py) 中使用 `@tool` 装饰器添加即可，Agent 会自动发现：

```python
@tool
def my_new_tool(param: str) -> str:
    """工具描述 — Agent 靠这段描述判断何时调用。"""
    return f"结果：{param}"

ALL_TOOLS.append(my_new_tool)
```

---

## 📡 API 接口

### `GET /health`

健康检查。

```json
{"status": "ok", "service": "ai-agent-backend", "version": "1.0.0"}
```

### `POST /chat`

发送 prompt 给 Agent，支持多轮对话记忆。

**请求体：**
```json
{
  "prompt": "北京天气怎么样？",
  "thread_id": "my-session"
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | ✅ | 用户提示词 |
| `thread_id` | string | ❌ | 会话 ID（默认 `"default"`），相同 ID 共享对话历史 |

**响应体：**
```json
{"answer": "🌍 北京 当前天气：晴\n🌡️ 温度：28°C\n💧 湿度：45%"}
```

> 💡 **多轮对话**：传入相同的 `thread_id`，Agent 会记住之前的对话内容，实现连续追问。

---

## 🧱 技术栈

- **[FastAPI](https://fastapi.tiangolo.com/)** — 高性能异步 Web 框架
- **[LangChain v1](https://docs.langchain.com/oss/python/langchain/overview)** — LLM 应用框架，使用 `create_agent` 最新 API
- **[LangGraph](https://www.langchain.com/langgraph)** — Agent 状态图引擎，提供 `InMemorySaver` 实现对话状态持久化
- **[DeepSeek](https://platform.deepseek.com/)** — 默认 LLM（OpenAI 兼容接口，可替换为 OpenAI / vLLM / OneAPI）
- **[Pydantic](https://docs.pydantic.dev/)** — 数据验证与序列化

---

## 📄 License

MIT — 可自由使用、修改和分发。
