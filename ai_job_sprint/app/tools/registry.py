from app.tools.calculator import calculator
from app.tools.weather import weather
from app.tools.mock_search import mock_search
from app.tools.database import database_query

from app.tools.rag_tool import rag_search
from app.tools.sql_tool import query_articles
from app.tools.news_tool import fetch_latest_posts

from app.schemas.agent import (
    CalculatorArgs,
    WeatherArgs,
    SearchArgs,
    DatabaseQueryArgs,
)

# =========================================================
# 1. Python 真正可以执行的工具
# =========================================================

TOOL_REGISTRY = {
    "calculator": calculator,
    "weather": weather,
    "mock_search": mock_search,
    "database_query": database_query,
    # Day7 新增
    "rag_search": rag_search,
    "query_articles": query_articles,
    "fetch_latest_posts": fetch_latest_posts,
}


# =========================================================
# 2. 工具参数校验模型
# =========================================================

TOOL_ARGUMENT_SCHEMAS = {
    "calculator": CalculatorArgs,
    "weather": WeatherArgs,
    "mock_search": SearchArgs,
    "database_query": DatabaseQueryArgs,
}


# =========================================================
# 3. 给 LLM 看的“工具说明书”
# =========================================================

TOOL_DEFINITIONS = [
    # -----------------------------------------------------
    # calculator
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "calculator",
        "description": "执行基础数学计算。用户需要进行加减乘除计算时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "需要计算的数学表达式，例如 18 * 27",
                }
            },
            "required": ["expression"],
        },
    },
    # -----------------------------------------------------
    # weather
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "weather",
        "description": "查询指定城市的模拟天气信息。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如北京、广州、上海",
                }
            },
            "required": ["city"],
        },
    },
    # -----------------------------------------------------
    # mock_search
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "mock_search",
        "description": "搜索本地模拟知识数据，适合查询 FastAPI、RAG、Tool Calling 等资料。",
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
    # -----------------------------------------------------
    # database_query
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "database_query",
        "description": "根据部门名称查询员工数据。",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "部门名称，例如 AI 或 Backend",
                }
            },
            "required": ["department"],
        },
    },
    # =====================================================
    # Day7 新增工具
    # =====================================================
    # -----------------------------------------------------
    # rag_search
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "rag_search",
        "description": "查询企业知识库。当用户询问公司制度、员工福利、报销规定、内部资料等知识库内容时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "需要查询的企业知识库问题",
                }
            },
            "required": ["question"],
        },
    },
    # -----------------------------------------------------
    # query_articles
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "query_articles",
        "description": "查询数据库中的文章或业务数据。当用户需要查询结构化数据库信息时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "需要查询的关键词",
                }
            },
            "required": ["keyword"],
        },
    },
    # -----------------------------------------------------
    # fetch_latest_posts
    # -----------------------------------------------------
    {
        "type": "function",
        "name": "fetch_latest_posts",
        "description": "获取最新资讯或公开信息。当用户需要查询最新动态、新闻或资讯时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "需要查询的资讯关键词",
                }
            },
            "required": ["keyword"],
        },
    },
]
