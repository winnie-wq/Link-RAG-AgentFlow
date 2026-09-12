import asyncio
import json
import logging
import time


from app.services.llm_client import LLMClient
from app.core.config import ARK_MODEL
from app.tools.registry import (
    TOOL_REGISTRY,
    TOOL_ARGUMENT_SCHEMAS,
    TOOL_DEFINITIONS,
)

logger = logging.getLogger(__name__)


TOOL_TIMEOUT = 5


class ToolAgent:

    def __init__(self):

        self.llm = LLMClient()

    # ==========================
    # 第一轮请求模型
    # ==========================

    async def _first_response(
        self,
        message: str,
    ):

        response = await asyncio.to_thread(
            self.llm.client.responses.create,
            model=ARK_MODEL,
            store=True,
            input=[
                {
                    "type": "message",
                    "role": "user",
                    "content": message,
                }
            ],
            tools=TOOL_DEFINITIONS,
        )

        return response

    # ==========================
    # 查找 function_call
    # ==========================

    def _find_function_call(
        self,
        response,
    ):

        for item in response.output:

            if item.type == "function_call":

                return item

        return None

    # ==========================
    # 提取普通文本
    # ==========================

    def _extract_message_text(
        self,
        response,
    ) -> str:

        for item in response.output:

            if item.type != "message":

                continue

            texts = []

            for content in item.content:

                if content.type == "output_text":

                    texts.append(content.text)

            if texts:

                return "".join(texts)

        return ""

    # ==========================
    # 解析工具参数
    # ==========================

    def _parse_arguments(
        self,
        function_call,
    ):

        try:

            return json.loads(function_call.arguments)

        except json.JSONDecodeError as exc:

            raise ValueError("模型生成非法 JSON 参数") from exc

    # ==========================
    # 工具白名单检查
    # ==========================

    def _validate_tool_name(
        self,
        tool_name: str,
    ):

        if tool_name not in TOOL_REGISTRY:

            raise ValueError(f"非法工具:{tool_name}")

    # ==========================
    # 参数校验
    # ==========================

    def _validate_arguments(
        self,
        tool_name,
        arguments,
    ):

        schema = TOOL_ARGUMENT_SCHEMAS[tool_name]

        validated = schema.model_validate(arguments)

        return validated.model_dump()

    # ==========================
    # 执行 Python 工具
    # ==========================

    async def _execute_tool(
        self,
        tool_name,
        arguments,
    ):

        function = TOOL_REGISTRY[tool_name]

        start = time.perf_counter()

        try:

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    function,
                    **arguments,
                ),
                timeout=TOOL_TIMEOUT,
            )

            logger.info("Tool success %s", tool_name)

            return {
                "success": True,
                "data": result,
            }

        except Exception as exc:

            logger.exception("Tool failed")

            return {
                "success": False,
                "error": str(exc),
            }

    # ==========================
    # 第二轮，把工具结果给模型
    # ==========================

    async def _second_response(
        self,
        previous_response_id,
        call_id,
        tool_output,
    ):

        response = await asyncio.to_thread(
            self.llm.client.responses.create,
            model=ARK_MODEL,
            previous_response_id=previous_response_id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(
                        tool_output,
                        ensure_ascii=False,
                    ),
                }
            ],
        )

        return response

    # ==========================
    # Agent 主流程
    # ==========================

    async def run(
        self,
        message: str,
    ):

        # 1. 用户问题 -> 模型

        first_response = await self._first_response(message)

        # 2. 判断是否需要工具

        function_call = self._find_function_call(first_response)

        # ======================
        # 普通回答
        # ======================

        if function_call is None:

            return {
                "answer": self._extract_message_text(first_response),
                "tool_used": None,
                "tool_result": None,
            }

        # ======================
        # 工具调用流程
        # ======================

        tool_name = function_call.name

        self._validate_tool_name(tool_name)

        arguments = self._parse_arguments(function_call)

        validated_arguments = self._validate_arguments(
            tool_name,
            arguments,
        )

        tool_result = await self._execute_tool(
            tool_name,
            validated_arguments,
        )

        second_response = await self._second_response(
            previous_response_id=first_response.id,
            call_id=function_call.call_id,
            tool_output=tool_result,
        )

        final_answer = self._extract_message_text(second_response)

        return {
            "answer": final_answer,
            "tool_used": tool_name,
            "tool_result": tool_result,
        }
