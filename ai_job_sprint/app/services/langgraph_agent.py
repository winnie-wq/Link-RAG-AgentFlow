import asyncio
import json
import logging
import time

from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from app.core.config import ARK_MODEL

from app.services.llm_client import (
    LLMClient,
)

from app.tools.registry import (
    TOOL_REGISTRY,
    TOOL_ARGUMENT_SCHEMAS,
    TOOL_DEFINITIONS,
)

logger = logging.getLogger(__name__)


# =========================================================
# 配置
# =========================================================

TOOL_TIMEOUT = 5

TOOL_MAX_RETRIES = 2

MAX_STEPS = 6


# =========================================================
# LangGraph State
# =========================================================


class AgentState(
    TypedDict,
    total=False,
):

    # 用户原始问题
    message: str

    # Ark Responses API 上一轮 response id
    response_id: str | None

    # Function Calling 的 call_id
    call_id: str | None

    # 模型选择的工具名称
    tool_name: str | None

    # 模型生成的工具参数
    arguments: dict | None

    # Python 工具执行结果
    tool_result: dict | None

    last_tool_name: str | None

    last_tool_result: dict | None

    # 最终回答
    answer: str

    # Graph 当前执行步数
    step_count: int

    # 错误信息
    error: str | None


# =========================================================
# LangGraph Agent
# =========================================================


class LangGraphAgent:

    def __init__(self):

        # Day1 已经实现好的 LLMClient
        self.llm = LLMClient()

        # LangGraph Checkpointer
        #
        # 作用：
        # 保存不同 thread_id 对应的 Graph State。
        #
        # 当前是内存版：
        # 服务重启后数据会消失。
        self.checkpointer = InMemorySaver()

        # 构建 Graph
        self.graph = self._build_graph()

    # =====================================================
    # Node 1：Agent / LLM Node
    # =====================================================

    async def agent_node(
        self,
        state: AgentState,
    ):
        """
        Agent Node 的职责：

        1. 第一次进入：
            用户问题 -> LLM

        2. Tool 执行完成以后再次进入：
            function_call_output -> LLM

        3. 解析模型输出：
            - function_call
            - 普通 message
        """

        current_step = state.get(
            "step_count",
            0,
        )

        # ---------------------------------------------
        # 最大执行步数限制
        # ---------------------------------------------

        if current_step >= MAX_STEPS:

            return {
                "answer": "Agent 已达到最大执行步数，任务停止。",
                "error": "MAX_STEPS_EXCEEDED",
                "tool_name": None,
                "step_count": current_step,
            }

        # ---------------------------------------------
        # 判断：
        #
        # 是第一次调用模型？
        #
        # 还是 Tool 执行完成后再次调用模型？
        # ---------------------------------------------

        has_tool_result = (
            state.get("tool_result") is not None
            and state.get("call_id") is not None
            and state.get("response_id") is not None
        )

        # =================================================
        # 情况 A：
        # 第一次调用模型
        # =================================================

        if not has_tool_result:

            logger.info(
                "LangGraph agent first LLM call " "step=%s",
                current_step + 1,
            )

            response = await asyncio.to_thread(
                self.llm.client.responses.create,
                model=ARK_MODEL,
                store=True,
                input=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": state["message"],
                    }
                ],
                tools=TOOL_DEFINITIONS,
            )

        # =================================================
        # 情况 B：
        # Tool 已执行完成
        #
        # 把 function_call_output 回传模型
        # =================================================

        else:

            logger.info(
                "LangGraph agent second LLM call " "tool=%s step=%s",
                state.get("tool_name"),
                current_step + 1,
            )

            response = await asyncio.to_thread(
                self.llm.client.responses.create,
                model=ARK_MODEL,
                previous_response_id=state["response_id"],
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": state["call_id"],
                        "output": json.dumps(
                            state["tool_result"],
                            ensure_ascii=False,
                        ),
                    }
                ],
            )

        # =================================================
        # 解析模型输出
        # =================================================

        for item in response.output:

            # ---------------------------------------------
            # 模型选择了工具
            # ---------------------------------------------

            if item.type == "function_call":

                try:

                    arguments = json.loads(item.arguments)

                except json.JSONDecodeError:

                    logger.error(
                        "Model returned invalid " "tool arguments: %s",
                        item.arguments,
                    )

                    return {
                        "answer": "模型生成的工具参数格式错误。",
                        "error": "INVALID_TOOL_ARGUMENT_JSON",
                        "tool_name": None,
                        "step_count": current_step + 1,
                    }

                logger.info(
                    "Model selected tool=%s " "arguments=%s",
                    item.name,
                    arguments,
                )

                return {
                    # 保存这一轮 Response ID
                    "response_id": response.id,
                    # 保存 Function Call ID
                    "call_id": item.call_id,
                    # 工具名称
                    "tool_name": item.name,
                    # 工具参数
                    "arguments": arguments,
                    # 清掉上一轮工具结果
                    "tool_result": None,
                    # 当前还没有最终答案
                    "answer": "",
                    # 清除旧错误
                    "error": None,
                    "step_count": current_step + 1,
                }

            # ---------------------------------------------
            # 模型直接生成最终回答
            # ---------------------------------------------

            if item.type == "message":

                text = ""

                for content in item.content:

                    if content.type == "output_text":

                        text += content.text

                logger.info(
                    "Agent produced final answer " "step=%s",
                    current_step + 1,
                )

                return {
                    "answer": text,
                    # 很关键：
                    # 清掉旧 tool_name，
                    # 否则 Conditional Edge
                    # 可能误以为还要继续调用工具。
                    "tool_name": None,
                    "arguments": None,
                    "call_id": None,
                    "tool_result": None,
                    "error": None,
                    "step_count": current_step + 1,
                }

        # ---------------------------------------------
        # 模型返回了无法识别的结构
        # ---------------------------------------------

        return {
            "answer": "模型没有返回可处理的内容。",
            "error": "EMPTY_MODEL_OUTPUT",
            "tool_name": None,
            "step_count": current_step + 1,
        }

    # =====================================================
    # Conditional Edge：
    # Agent 执行完后决定下一站
    # =====================================================

    def route_after_agent(
        self,
        state: AgentState,
    ):
        """
        如果模型选择了工具：
            agent -> tools

        如果已经有最终 answer：
            agent -> END

        如果发生错误：
            agent -> END
        """

        # 出错直接结束
        if state.get("error"):

            return "end"

        # 最大执行步数
        if (
            state.get(
                "step_count",
                0,
            )
            >= MAX_STEPS
        ):

            return "end"

        # 模型选择了 Tool
        if state.get("tool_name"):

            return "tools"

        # 没有 Tool
        # 说明已经生成最终回答
        return "end"

    # =====================================================
    # Tool 参数验证
    # =====================================================

    def _validate_arguments(
        self,
        tool_name: str,
        arguments: dict,
    ):

        schema = TOOL_ARGUMENT_SCHEMAS[tool_name]

        validated = schema.model_validate(arguments)

        return validated.model_dump()

    # =====================================================
    # Tool 执行 + Timeout + Retry
    # =====================================================

    async def _execute_tool_with_retry(
        self,
        function,
        arguments: dict,
    ):

        last_error = None

        for attempt in range(TOOL_MAX_RETRIES):

            start = time.perf_counter()

            try:

                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        function,
                        **arguments,
                    ),
                    timeout=TOOL_TIMEOUT,
                )

                latency = time.perf_counter() - start

                logger.info(
                    "Tool execution success " "attempt=%s latency=%.2fs",
                    attempt + 1,
                    latency,
                )

                return result

            except Exception as exc:

                latency = time.perf_counter() - start

                last_error = exc

                logger.warning(
                    "Tool execution failed " "attempt=%s " "latency=%.2fs " "error=%s",
                    attempt + 1,
                    latency,
                    str(exc),
                )

                if attempt < TOOL_MAX_RETRIES - 1:

                    await asyncio.sleep(2**attempt)

        raise last_error

    # =====================================================
    # Node 2：Tool Node
    # =====================================================

    async def tool_node(
        self,
        state: AgentState,
    ):
        """
        Tool Node：

        1. 获取 tool_name
        2. 工具白名单
        3. 参数验证
        4. 获取 Python Function
        5. timeout + retry
        6. 执行工具
        7. 把结果写回 State
        """

        tool_name = state.get("tool_name")

        arguments = state.get("arguments")

        # ---------------------------------------------
        # 没有工具名称
        # ---------------------------------------------

        if not tool_name:

            return {
                "error": "TOOL_NAME_MISSING",
                "answer": "模型没有提供工具名称。",
            }

        # ---------------------------------------------
        # 工具白名单
        # ---------------------------------------------

        if tool_name not in TOOL_REGISTRY:

            logger.error(
                "Tool not allowed: %s",
                tool_name,
            )

            return {
                "error": f"TOOL_NOT_ALLOWED:{tool_name}",
                "answer": f"工具 {tool_name} 不在允许列表中。",
            }

        # ---------------------------------------------
        # 参数必须存在
        # ---------------------------------------------

        if arguments is None:

            return {
                "error": "TOOL_ARGUMENTS_MISSING",
                "answer": "模型没有提供工具参数。",
            }

        # ---------------------------------------------
        # Pydantic 参数验证
        # ---------------------------------------------

        try:

            validated_arguments = self._validate_arguments(
                tool_name,
                arguments,
            )

        except Exception as exc:

            logger.exception("Tool argument validation failed")

            # 这里不让整个 API 崩掉。
            #
            # 把错误作为 Tool Result
            # 返回给模型，让模型解释。
            return {
                "tool_result": {
                    "success": False,
                    "error": "工具参数验证失败",
                    "detail": str(exc),
                },
                "error": None,
            }

        # ---------------------------------------------
        # 从 Registry 找到真正 Python 函数
        # ---------------------------------------------

        function = TOOL_REGISTRY[tool_name]

        # ---------------------------------------------
        # 真正执行 Python Tool
        # ---------------------------------------------

        try:

            result = await self._execute_tool_with_retry(
                function,
                validated_arguments,
            )

            tool_result = {
                "success": True,
                "data": result,
            }

        except Exception as exc:

            logger.exception("Tool failed after retries")

            tool_result = {
                "success": False,
                "error": str(exc),
            }

        # ---------------------------------------------
        # Tool Node 不负责生成最终答案
        #
        # 它只负责把结果写入 State。
        # ---------------------------------------------

        return {
            "tool_result": tool_result,
            "last_tool_name": tool_name,
            "last_tool_result": tool_result,
            "error": None,
        }

    # =====================================================
    # Tool 后面的路由
    # =====================================================

    def route_after_tool(
        self,
        state: AgentState,
    ):
        """
        Tool 执行完成以后：

        正常：
            tools -> agent

        严重错误：
            tools -> END
        """

        if state.get("error"):

            return "end"

        return "agent"

    # =====================================================
    # Build Graph
    # =====================================================

    def _build_graph(self):

        builder = StateGraph(AgentState)

        # ---------------------------------------------
        # 注册 Node
        # ---------------------------------------------

        builder.add_node(
            "agent",
            self.agent_node,
        )

        builder.add_node(
            "tools",
            self.tool_node,
        )

        # ---------------------------------------------
        # START -> agent
        # ---------------------------------------------

        builder.add_edge(
            START,
            "agent",
        )

        # ---------------------------------------------
        # agent 后面是条件分支
        #
        # 有工具：
        #     agent -> tools
        #
        # 已回答 / 出错：
        #     agent -> END
        # ---------------------------------------------

        builder.add_conditional_edges(
            "agent",
            self.route_after_agent,
            {
                "tools": "tools",
                "end": END,
            },
        )

        # ---------------------------------------------
        # Tool 执行以后：
        #
        # 正常：
        #     回到 agent
        #
        # 严重错误：
        #     END
        # ---------------------------------------------

        builder.add_conditional_edges(
            "tools",
            self.route_after_tool,
            {
                "agent": "agent",
                "end": END,
            },
        )

        # ---------------------------------------------
        # compile
        #
        # 加上 checkpointer 后，
        # Graph 可以根据 thread_id
        # 保存不同线程的状态。
        # ---------------------------------------------

        return builder.compile(checkpointer=self.checkpointer)

    # =====================================================
    # 对外统一入口
    # =====================================================

    async def run(
        self,
        message: str,
        thread_id: str,
    ):
        """
        FastAPI 不需要知道 Graph 内部细节。

        API 只需要：

            await agent.run(...)
        """

        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "message": message,
            "answer": "",
            "tool_name": None,
            "arguments": None,
            "tool_result": None,
            "last_tool_name": None,
            "last_tool_result": None,
            "call_id": None,
            "response_id": None,
            "error": None,
            "step_count": 0,
        }

        result = await self.graph.ainvoke(
            initial_state,
            config=config,
        )

        return {
            "answer": result.get(
                "answer",
                "",
            ),
            "tool_used": result.get("last_tool_name"),
            "tool_result": result.get("last_tool_result"),
            "error": result.get("error"),
            "step_count": result.get(
                "step_count",
                0,
            ),
        }
