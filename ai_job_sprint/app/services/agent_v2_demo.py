from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END,
)


class DemoState(
    TypedDict,
    total=False,
):
    question: str
    route: str
    answer: str


def router_node(
    state: DemoState,
):

    question = state["question"]

    if "公司" in question:
        route = "rag"

    elif "数据库" in question:
        route = "sql"

    elif "天气" in question:
        route = "api"

    else:
        route = "end"

    return {"route": route}


def rag_node(state):
    return {"answer": "这里执行 RAG 检索"}


def sql_node(state):
    return {"answer": "这里执行 SQL 查询"}


def api_node(state):
    return {"answer": "这里执行 API 查询"}


def route_after_router(state):

    return state["route"]


builder = StateGraph(DemoState)

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

builder.add_edge(
    START,
    "router",
)

builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "rag": "rag",
        "sql": "sql",
        "api": "api",
        "end": END,
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

graph = builder.compile()


if __name__ == "__main__":

    result = graph.invoke({"question": "公司的年假制度是什么？"})

    print(result)
