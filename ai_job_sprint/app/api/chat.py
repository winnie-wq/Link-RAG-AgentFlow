import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.llm_client import LLMClient
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ExtractRequest,
    NewsInfo,
)
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Chat"]
)

llm = LLMClient()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="普通模型对话",
    description="调用火山方舟大模型并一次性返回完整回答。"
)
async def chat(request: ChatRequest):

    try:

        answer = await llm.chat(
            request.message
        )

        return {
            "answer": answer
        }

    except asyncio.TimeoutError:

        raise HTTPException(
            status_code=504,
            detail="模型请求超时，请稍后重试",
        )

    except Exception as exc:

        logger.exception(
            "Chat request failed"
        )

        raise HTTPException(
            status_code=502,
            detail="模型服务调用失败",
        ) from exc

@router.post(
    "/extract",
    response_model=NewsInfo,
)
async def extract(
    request: ExtractRequest,
):

    try:

        result = await llm.extract_news(
            request.text
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Extract request failed"
        )

        raise HTTPException(
            status_code=502,
            detail="结构化信息抽取失败",
        ) from exc

@router.post(
    "/chat/stream",
    summary="流式模型对话",
    description="通过 SSE 持续返回模型增量输出。"
)
async def chat_stream(request: ChatRequest):

    async def event_generator():

        try:

            async for item in llm.stream_chat(
                request.message
            ):

                yield (
                    "data: "
                    + json.dumps(
                        item,
                        ensure_ascii=False,
                    )
                    + "\n\n"
                )

        except Exception as exc:

            logger.exception(
                "Streaming chat failed"
            )

            error_data = {
                "type": "error",
                "message": str(exc),
            }

            yield (
                "event: error\n"
                "data: "
                + json.dumps(
                    error_data,
                    ensure_ascii=False,
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )