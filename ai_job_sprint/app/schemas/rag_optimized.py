from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class OptimizedRAGRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="用户问题",
    )

    mode: Literal[
        "vector",
        "hybrid",
        "hybrid_rerank",
    ] = "hybrid_rerank"

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="最终返回给 LLM 的检索结果数量",
    )


class OptimizedRAGSource(BaseModel):

    source: str

    chunk_id: int

    retrieval_score: float


class OptimizedRAGResponse(BaseModel):

    answer: str

    sources: list[OptimizedRAGSource]

    mode: str
