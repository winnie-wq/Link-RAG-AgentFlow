import asyncio

from app.services.llm_client import LLMClient

PROMPTS = {
    "A": """
请回答用户的问题。
""",
    "B": """
请严格根据参考资料回答。

如果资料中没有答案，
请明确说明无法确定。

不要编造信息。
""",
}


QUESTION = "什么是 RAG？"

CONTEXT = """
RAG 是 Retrieval-Augmented Generation，
即检索增强生成。
它通过先检索外部资料，
再让大模型根据资料生成答案。
"""


async def evaluate():

    llm = LLMClient()

    for name, prompt in PROMPTS.items():

        full_prompt = f"""
{prompt}

【参考资料】
{CONTEXT}

【问题】
{QUESTION}
"""

        print("=" * 50)
        print("Prompt：", name)

        answer = await llm.chat(full_prompt)

        print("答案：")
        print(answer)


if __name__ == "__main__":
    asyncio.run(evaluate())
