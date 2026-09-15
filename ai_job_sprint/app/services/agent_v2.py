from typing import TypedDict
from app.core.runtime import (
    rag_service,
)

from app.tools.sql_tool import (
    query_articles,
)

from app.tools.news_tool import (
    fetch_latest_posts,
)
from app.services.llm_client import (
    LLMClient,
)
from langgraph.graph import (
    StateGraph,
    START,
    END,
)


class AgentV2State(
    TypedDict,
    total=False,
):

    question: str

    route: str

    tool_name: str

    tool_input: dict

    tool_output: object

    answer: str

    error: str

    step_count: int

    retry_count: int


def router_node(
    state: AgentV2State,
):

    question = state["question"].lower()

    if any(
        word in question
        for word in [
            "公司",
            "制度",
            "年假",
            "知识库",
        ]
    ):

        route = "rag"

    elif any(
        word in question
        for word in [
            "数据库",
            "记录",
            "文章",
        ]
    ):

        route = "sql"

    elif any(
        word in question
        for word in [
            "实时",
            "最新",
            "资讯",
        ]
    ):

        route = "api"

    else:

        route = "llm"

    return {
        "route": route,
        "step_count": state.get(
            "step_count",
            0,
        )
        + 1,
    }


async def rag_node(state):

    result = await rag_service.answer(
        question=state["question"],
        mode="hybrid_rerank",
        top_k=3,
    )

    return {
        "answer": result["answer"],
        "tool_name": "rag_search",
        "tool_output": result,
    }


def sql_node(state):

    result = query_articles(
        keyword=state["question"],
        limit=5,
    )

    return {
        "answer": str(result),
        "tool_name": "query_articles",
        "tool_output": result,
    }


def api_node(state):

    result = fetch_latest_posts()

    return {
        "answer": str(result),
        "tool_name": "fetch_latest_posts",
        "tool_output": result,
    }


llm = LLMClient()


async def llm_node(state):

    answer = await llm.chat(state["question"])

    return {
        "answer": answer,
        "tool_name": None,
    }


MAX_STEPS = 6


def guard_node(state):

    if (
        state.get(
            "step_count",
            0,
        )
        >= MAX_STEPS
    ):

        return {
            "error": "MAX_STEPS_EXCEEDED",
            "answer": "Agent 已达到最大执行步数。",
        }

    return {}


def route_after_router(state):

    return state["route"]


def build_graph():

    builder = StateGraph(AgentV2State)

    builder.add_node(
        "guard",
        guard_node,
    )

    builder.add_node(
        "router",
        router_node,
    )

    builder.add_node(
        "rag",
        rag_node,
    )

    builder.add_node(
        "sql",
        sql_node,
    )

    builder.add_node(
        "api",
        api_node,
    )

    builder.add_node(
        "llm",
        llm_node,
    )

    builder.add_edge(
        START,
        "guard",
    )

    builder.add_edge(
        "guard",
        "router",
    )

    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "rag": "rag",
            "sql": "sql",
            "api": "api",
            "llm": "llm",
        },
    )

    builder.add_edge(
        "rag",
        END,
    )

    builder.add_edge(
        "sql",
        END,
    )

    builder.add_edge(
        "api",
        END,
    )

    builder.add_edge(
        "llm",
        END,
    )

    return builder.compile()
