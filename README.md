# 🤖 AI Agent Backend Service

> 基于 LangGraph + FastAPI 的生产级 AI 智能体服务 | 支持多轮对话记忆、工具调用、容器化部署

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.3+-red.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-✅-blue.svg)](https://www.docker.com/)

---

## ✨ 核心能力

| 能力 | 说明 |
|------|------|
| 🧠 **智能 Agent** | 基于 LangGraph `create_agent`，自动理解意图、调用工具 |
| 💬 **多轮记忆** | `InMemorySaver` 实现会话级状态持久化，支持 thread_id 隔离 |
| 🔧 **工具扩展** | 内置天气查询、计算器，可轻松添加任意工具 |
| 🌐 **REST API** | FastAPI 服务，提供 `/chat`、`/health`、`/docs` 端点 |
| 📦 **容器化** | Docker + docker-compose 一键部署 |
| 📊 **批量处理** | CSV 输入 → Agent 处理 → CSV 输出，模拟 AI 工程化链路 |

---

## 🚀 快速开始

### 1. 克隆与配置

```bash
git clone https://github.com/yao-933/ai-agent-backend.git
cd ai-agent-backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
# DEEPSEEK_API_KEY=sk-xxx
# OPENAI_API_KEY=sk-xxx
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 测试调用

```bash
# 单轮对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "北京今天天气怎么样？"}'

# 多轮对话（同一个 thread_id 会记住上下文）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "100 divided by 4?", "thread_id": "test-001"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "multiply that by 6", "thread_id": "test-001"}'
# 返回 150 ✅
```

### 5. Docker 部署

```bash
docker build -t ai-agent-backend .
docker run -p 8000:8000 --env-file .env ai-agent-backend
```

---

## 📁 项目结构

```text
ai-agent-backend/
├── main.py              # FastAPI 入口
├── agent.py             # LangGraph Agent
├── tools.py             # 工具函数（天气、计算器）
├── models.py            # 请求/响应模型
├── batch_process.py     # CSV 批量处理
├── requirements.txt     # 依赖列表
├── Dockerfile           # Docker 镜像
├── docker-compose.yaml  # 容器编排
├── .env.example         # 环境变量模板
└── README.md            # 项目文档
```

---

## 🛠️ 技术栈

| 类别 | 技术 | 作用 |
|------|------|------|
| 后端框架 | FastAPI | REST API 服务 |
| AI 框架 | LangChain | 模型调用、工具定义 |
| Agent 图 | LangGraph | 状态管理、记忆持久化 |
| 大模型 | DeepSeek / Claude | 推理与对话 |
| 部署 | Docker | 容器化 |
| 文档 | Swagger UI | 交互式 API 文档 |

---

## 📊 API 文档

启动服务后访问：http://localhost:8000/docs

### POST /chat

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | ✅ | 用户输入的问题 |
| thread_id | string | ❌ | 会话 ID，传了则保持多轮记忆 |
| temperature | float | ❌ | 模型温度，默认 0.7 |

### GET /health

健康检查，返回 `{"status": "ok"}`

---

## 📝 技术亮点

✅ **生产级 Agent**：使用 LangGraph `create_agent` 替代手写循环

✅ **状态持久化**：`InMemorySaver` 实现会话级记忆

✅ **工程化部署**：Docker + 环境变量管理

✅ **可扩展架构**：在 `tools.py` 添加 `@tool` 即可扩展

✅ **批量处理链路**：支持 CSV 离线特征生产

---

## 📄 License

MIT
