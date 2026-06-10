"""
应用配置 — 所有环境变量集中管理，支持 .env 文件。
优先级：系统环境变量 > .env 文件 > 默认值
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Windows SSL 证书修复 ──────────────────────────────────────
# Windows 环境下 Python 经常找不到系统 CA 证书，导致所有 HTTPS
# 请求报 SSL: CERTIFICATE_VERIFY_FAILED。这里手动指定 certifi 的
# CA bundle 路径来解决。
if os.name == "nt":
    try:
        import certifi
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except ImportError:
        pass

# ── LLM / API 配置 ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-xxx")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")
# 如果你用的是 OpenAI 官方：把 BASE_URL 设为 https://api.openai.com/v1
# 如果你用的是其他兼容服务（如 OneAPI / vLLM），改成对应的地址即可

# ── 服务配置 ──────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
