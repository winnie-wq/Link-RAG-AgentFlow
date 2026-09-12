from app.tools.calculator import calculator
from app.tools.weather import weather
from app.tools.mock_search import mock_search
from app.tools.database import database_query
from app.schemas.agent import (
    CalculatorArgs,
    WeatherArgs,
    SearchArgs,
    DatabaseQueryArgs,
)

# Python 真正可以执行的工具
TOOL_REGISTRY = {
    "calculator": calculator,
    "weather": weather,
    "mock_search": mock_search,
    "database_query": database_query,
}

# 每个工具对应的参数校验模型
TOOL_ARGUMENT_SCHEMAS = {
    "calculator": CalculatorArgs,
    "weather": WeatherArgs,
    "mock_search": SearchArgs,
    "database_query": DatabaseQueryArgs,
}

# 给 LLM 的函数说明书
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "calculator",
        "description": ("执行基础数学计算。" "用户需要进行加减乘除计算时使用。"),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": ("需要计算的数学表达式，" "例如 18 * 27"),
                }
            },
            "required": ["expression"],
        },
    },
    {
        "type": "function",
        "name": "weather",
        "description": ("查询指定城市的模拟天气信息。"),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": ("城市名称，例如北京、广州、上海"),
                }
            },
            "required": ["city"],
        },
    },
    {
        "type": "function",
        "name": "mock_search",
        "description": (
            "搜索本地模拟知识数据。" "适合查询 FastAPI、RAG、Tool Calling 等资料。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "需要搜索的关键词",
                }
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "database_query",
        "description": ("根据部门名称查询员工数据。"),
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": ("部门名称，例如 AI 或 Backend"),
                }
            },
            "required": ["department"],
        },
    },
]
