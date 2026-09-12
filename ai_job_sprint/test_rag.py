import asyncio

from app.services.rag_service import (
    RAGService,
)


async def main():

    rag = RAGService()

    index_result = rag.index_text_document(
        file_path="data/company.md",
        chunk_size=100,
        overlap=20,
    )

    print(
        "索引结果：",
        index_result,
    )

    print()

    retrieved = rag.retrieve(
        question="员工有多少天年假？",
        top_k=3,
    )

    print("检索结果：")

    for item in retrieved:

        print(
            item["score"],
            item["text"],
        )

    print()

    result = await rag.answer(
        question="员工入职满一年后有多少天年假？",
        top_k=3,
    )

    print(
        "最终回答：",
        result,
    )


if __name__ == "__main__":

    asyncio.run(main())
