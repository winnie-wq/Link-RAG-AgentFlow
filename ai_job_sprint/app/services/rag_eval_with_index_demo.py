import asyncio
import time

from app.core.runtime import rag_service

QUESTIONS = [
    "什么是 RAG？",
    "什么是 Hybrid Search？",
    "什么是 MCP？",
]


async def evaluate():

    # 1. 先建立索引
    print("开始建立 RAG 索引...")

    index_result = rag_service.index_text_document(
        file_path="knowledge.txt",
        chunk_size=500,
        overlap=100,
    )

    print("索引建立成功！")
    print("来源：", index_result["source"])
    print("Chunk 数量：", index_result["chunk_count"])
    print("-" * 50)

    # 2. 开始评估
    success = 0
    total_latency = 0

    for question in QUESTIONS:

        start = time.perf_counter()

        try:

            result = await rag_service.answer(
                question=question,
                mode="hybrid_rerank",
                top_k=3,
            )

            latency = time.perf_counter() - start

            success += 1
            total_latency += latency

            print("问题：", question)
            print("答案：", result["answer"])
            print("来源：", result["sources"])
            print("耗时：", round(latency, 3), "秒")

        except Exception as exc:

            print("失败：", repr(exc))

        print("-" * 50)

    print(
        "成功率：",
        round(success / len(QUESTIONS) * 100, 2),
        "%",
    )

    if success:
        print(
            "平均延迟：",
            round(total_latency / success, 3),
            "秒",
        )


if __name__ == "__main__":
    asyncio.run(evaluate())
