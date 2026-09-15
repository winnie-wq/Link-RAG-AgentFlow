from app.core.runtime import (
    rag_service,
)


async def rag_search(
    question: str,
):

    result = await rag_service.answer(
        question=question,
        mode="hybrid_rerank",
        top_k=3,
    )

    return result
