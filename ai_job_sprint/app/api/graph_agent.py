import logging

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.graph_agent import (
    GraphAgentRequest,
    GraphAgentResponse,
)

from app.services.langgraph_agent import (
    LangGraphAgent,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["LangGraph Agent"],
)


agent = LangGraphAgent()


@router.post(
    "/graph-agent",
    response_model=GraphAgentResponse,
    summary="LangGraph Tool Calling Agent",
)
async def run_graph_agent(
    request: GraphAgentRequest,
):

    try:

        result = await agent.run(
            message=request.message,
            thread_id=request.thread_id,
        )

        return GraphAgentResponse(**result)

    except Exception as exc:

        logger.exception("LangGraph Agent request failed")

        raise HTTPException(
            status_code=500,
            detail="LangGraph Agent 执行失败",
        ) from exc
