import asyncio
import json
import logging
import queue
import threading
import time

from pydantic import ValidationError
from volcenginesdkarkruntime import Ark

from app.schemas.chat import NewsInfo

from app.core.config import (
    ARK_API_KEY,
    ARK_MODEL,
    LLM_TIMEOUT,
    LLM_MAX_RETRIES,
)

logger = logging.getLogger(__name__)


class LLMClient:

    def __init__(self):

        if not ARK_API_KEY:
            raise ValueError("没有读取到 ARK_API_KEY")

        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=ARK_API_KEY,
        )

        # 保存模型名称
        self.model = ARK_MODEL

    # =====================================================
    # 普通同步调用
    # =====================================================

    def _chat_sync(self, message: str):

        response = self.client.responses.create(
            model=self.model,
            input=message,
        )

        answer = ""

        for item in response.output:

            if item.type == "message":

                for content in item.content:

                    if content.type == "output_text":
                        answer += content.text

        return answer, response

    # =====================================================
    # 普通异步调用
    # =====================================================

    async def chat(self, message: str):

        last_error = None

        for attempt in range(LLM_MAX_RETRIES):

            start = time.perf_counter()

            try:

                logger.info(
                    "LLM request started model=%s attempt=%s",
                    self.model,
                    attempt + 1,
                )

                answer, response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._chat_sync,
                        message,
                    ),
                    timeout=LLM_TIMEOUT,
                )

                latency = time.perf_counter() - start

                usage = getattr(response, "usage", None)

                logger.info(
                    "Token usage=%s",
                    usage,
                )

                logger.info(
                    "LLM request success model=%s latency=%.2fs",
                    self.model,
                    latency,
                )

                return answer

            except Exception as exc:

                latency = time.perf_counter() - start

                last_error = exc

                logger.warning(
                    "LLM request failed attempt=%s latency=%.2fs error=%s",
                    attempt + 1,
                    latency,
                    str(exc),
                )

                if attempt < LLM_MAX_RETRIES - 1:

                    delay = 2**attempt

                    await asyncio.sleep(delay)

        raise last_error

    # =====================================================
    # 结构化信息抽取
    # =====================================================

    async def extract_news(
        self,
        text: str,
    ) -> NewsInfo:

        schema = NewsInfo.model_json_schema()

        prompt = f"""
你是一个新闻信息抽取助手。

请从下面文本中提取信息。

必须只返回合法 JSON。
不要返回 Markdown。
不要添加解释。

JSON Schema：
{json.dumps(schema, ensure_ascii=False)}

新闻文本：
{text}
"""

        raw_answer = await self.chat(prompt)

        try:

            data = json.loads(raw_answer)

        except json.JSONDecodeError as exc:

            logger.error(
                "Model returned invalid JSON: %s",
                raw_answer,
            )

            raise ValueError("模型返回的不是合法 JSON") from exc

        try:

            return NewsInfo.model_validate(data)

        except ValidationError as exc:

            logger.error(
                "Structured output validation failed: %s",
                exc,
            )

            raise ValueError("模型返回 JSON，但结构不符合要求") from exc

    # =====================================================
    # Token 使用量转换
    # =====================================================

    def _usage_to_dict(self, usage):

        if usage is None:
            return None

        if hasattr(usage, "model_dump"):
            return usage.model_dump()

        if hasattr(usage, "dict"):
            return usage.dict()

        return str(usage)

    # =====================================================
    # 流式调用
    # =====================================================

    def _stream_chat_sync(self, message: str):

        stream = self.client.responses.create(
            model=self.model,
            input=message,
            stream=True,
        )

        for event in stream:

            if event.type == "response.reasoning_summary_text.delta":

                yield {
                    "type": "reasoning",
                    "delta": event.delta,
                }

            elif event.type == "response.output_text.delta":

                yield {
                    "type": "answer",
                    "delta": event.delta,
                }

            elif event.type == "response.completed":

                usage = self._usage_to_dict(event.response.usage)

                logger.info(
                    "Streaming completed usage=%s",
                    usage,
                )

                yield {
                    "type": "completed",
                    "usage": usage,
                }

    async def stream_chat(self, message: str):

        event_queue = queue.Queue()

        END = object()

        def worker():

            try:

                for item in self._stream_chat_sync(message):

                    event_queue.put(item)

            except Exception as exc:

                event_queue.put(exc)

            finally:

                event_queue.put(END)

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

        while True:

            item = await asyncio.to_thread(event_queue.get)

            if item is END:
                break

            if isinstance(item, Exception):
                raise item

            yield item

    # =====================================================
    # 多模态：文字 + 图片
    # =====================================================

    async def multimodal_chat(
        self,
        *,
        text: str,
        image_url: str,
    ):

        response = await asyncio.to_thread(
            self.client.responses.create,
            model=self.model,
            input=[
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text,
                        },
                        {
                            "type": "input_image",
                            "image_url": image_url,
                        },
                    ],
                }
            ],
        )

        for item in response.output:

            if item.type != "message":
                continue

            for content in item.content:

                if content.type == "output_text":

                    return content.text

        return ""
