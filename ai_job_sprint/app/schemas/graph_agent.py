from pydantic import BaseModel, Field


class GraphAgentRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="用户发送给 Agent 的问题",
    )

    thread_id: str = Field(
        default="default-thread",
        min_length=1,
        max_length=100,
        description="LangGraph 会话线程 ID",
    )


class GraphAgentResponse(BaseModel):

    answer: str

    tool_used: str | None = None

    tool_result: dict | None = None

    error: str | None = None

    step_count: int = 0
