import logging

from fastapi import APIRouter, HTTPException

from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
)

from app.services.tool_agent import ToolAgent


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


agent = ToolAgent()


@router.post(
    "",
    response_model=AgentResponse,
    summary="Tool Calling Agent",
)
async def run_agent(
    request: AgentRequest,
):

    try:

        result = await agent.run(
            request.message
        )

        return result

    except Exception as exc:

        logger.exception(
            "Agent request failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Agent 执行失败",
        ) from exc