from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END,
)


class DemoState(TypedDict):
    message: str
    answer: str


def process_message(
    state: DemoState,
):

    message = state["message"]

    return {"answer": f"收到你的消息：{message}"}


# 创建一个 LangGraph 流程设计器，并告诉它，这个流程中传递的数据遵循 DemoState
builder = StateGraph(DemoState)


builder.add_node(
    "process",
    process_message,
)


builder.add_edge(
    START,
    "process",
)


builder.add_edge(
    "process",
    END,
)

"""这里的 compile() 更像：

把我们刚才声明的 State、Node、Edge 整理并检查，
生成一个真正可以运行的 Graph 对象"""

graph = builder.compile()

if __name__ == "__main__":

    result = graph.invoke(
        {
            "message": "你好",
            "answer": "",
        }
    )

    print(result)
