from pydantic import (
    BaseModel,
    Field,
)


class RAGRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class RAGSource(BaseModel):

    source: str

    chunk_id: int

    score: float


class RAGResponse(BaseModel):

    answer: str

    sources: list[RAGSource]
