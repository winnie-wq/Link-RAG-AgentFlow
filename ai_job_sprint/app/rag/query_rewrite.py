import json

from app.services.llm_client import (
    LLMClient,
)


class QueryRewriter:

    def __init__(self):

        self.llm = LLMClient()

    async def rewrite(
        self,
        query: str,
        history: str = "",
    ):

        prompt = f"""
你是一个 RAG 检索查询改写器。

目标：
把用户问题改写成更适合知识库检索的独立问题。

要求：
1. 保留用户原始意图。
2. 不允许补充不存在的事实。
3. 如果原问题已经清晰，可以保持原意。
4. 只返回 JSON。
5. 格式：

{{
    "query": "改写后的查询"
}}

对话上下文：
{history}

用户问题：
{query}
"""

        raw = await self.llm.chat(prompt)

        try:

            data = json.loads(raw)

            return data["query"]

        except Exception:

            # Rewrite 失败时
            # 不让整个 RAG 挂掉
            return query
