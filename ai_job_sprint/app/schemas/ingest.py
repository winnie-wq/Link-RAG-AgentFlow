from pydantic import (
    BaseModel,
    Field,
)


class IngestRequest(BaseModel):

    source_url: str

    pages: int = Field(
        default=1,
        ge=1,
        le=10,
    )


class IngestResponse(BaseModel):

    inserted: int

    updated: int

    unchanged: int

    failed: int

    total: int

    rag: dict
