"""
Agent 工具定义 — 天气查询 + 简单计算器。

所有工具使用 LangChain @tool 装饰器注册，Agent 会自动根据
用户意图决定调用哪个工具。
"""

import re
import operator
from langchain_core.tools import tool

# ── 模拟天气数据 ──────────────────────────────────────────────
# 生产环境应替换为真实 API（如 OpenWeatherMap / 和风天气）

MOCK_WEATHER: dict[str, dict] = {
    "beijing":      {"temp": 28, "desc": "Sunny",        "humidity": 45},
    "shanghai":     {"temp": 30, "desc": "Cloudy",        "humidity": 65},
    "shenzhen":     {"temp": 32, "desc": "Showers",       "humidity": 78},
    "guangzhou":    {"temp": 31, "desc": "Thunderstorm",  "humidity": 80},
    "hangzhou":     {"temp": 27, "desc": "Light Rain",    "humidity": 70},
    "chengdu":      {"temp": 24, "desc": "Overcast",      "humidity": 75},
    "tokyo":        {"temp": 25, "desc": "Clear",         "humidity": 55},
    "new york":     {"temp": 22, "desc": "Partly Cloudy", "humidity": 60},
    "london":       {"temp": 15, "desc": "Rainy",         "humidity": 82},
    "paris":        {"temp": 18, "desc": "Fair",          "humidity": 58},
    "sydney":       {"temp": 20, "desc": "Windy",         "humidity": 50},
    "singapore":    {"temp": 31, "desc": "Thunderstorm",  "humidity": 85},
    # 中文别名
    "北京": {"temp": 28, "desc": "晴",   "humidity": 45},
    "上海": {"temp": 30, "desc": "多云",  "humidity": 65},
    "深圳": {"temp": 32, "desc": "阵雨",  "humidity": 78},
    "广州": {"temp": 31, "desc": "雷阵雨", "humidity": 80},
    "杭州": {"temp": 27, "desc": "小雨",  "humidity": 70},
    "成都": {"temp": 24, "desc": "阴天",  "humidity": 75},
}


@tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气。
    参数 city: 城市名称（中文或英文均可，例如 "北京" / "beijing" / "tokyo"）。
    返回该城市的温度、天气状况和湿度。
    """
    key = city.strip().lower()
    data = MOCK_WEATHER.get(key)
    if data is None:
        return (
            f"⚠️ 暂无「{city}」的天气数据。支持的城市："
            + "、".join(sorted({c.title() for c in MOCK_WEATHER}))
        )
    return (
        f"🌍 {city} 当前天气：{data['desc']}\n"
        f"🌡️ 温度：{data['temp']}°C\n"
        f"💧 湿度：{data['humidity']}%"
    )


# ── 安全计算器 ────────────────────────────────────────────────

def _safe_eval(expression: str) -> float:
    """安全地求值一个纯数学表达式。

    仅允许数字、运算符、括号和空格，禁止任何函数调用或变量访问，
    防止代码注入。
    """
    sanitized = expression.strip()
    if not re.match(r'^[\d\s+\-*/().%^]+$', sanitized):
        raise ValueError(f"表达式包含非法字符（仅允许数字和 + - * / ( ) . % ^）：{expression}")
    # 用受限的全局/局部命名空间执行 eval，阻断 __builtins__
    sanitized = sanitized.replace("^", "**")
    return eval(sanitized, {"__builtins__": {}}, {})


@tool
def calculator(expression: str) -> str:
    """计算一个数学表达式。
    参数 expression: 纯数学表达式字符串，例如 "1+2*3"、"2**10"、"sqrt(4)"。
    支持运算符：+ - * / ** ( ) . % ^
    """
    try:
        result = _safe_eval(expression)
        # 整数就不显示小数点
        if isinstance(result, float) and result == int(result):
            result = int(result)
        return f"📐 {expression} = {result}"
    except ValueError as e:
        return f"❌ 表达式错误：{e}"
    except ZeroDivisionError:
        return "❌ 数学错误：不能除以 0"
    except Exception as e:
        return f"❌ 计算出错：{e}"


# ── 工具注册表 ────────────────────────────────────────────────
# Agent 初始化时从此处获取全部工具列表

ALL_TOOLS = [get_weather, calculator]
