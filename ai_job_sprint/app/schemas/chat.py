#数据校验
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )

class ChatResponse(BaseModel):
    answer: str

class ExtractRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class NewsInfo(BaseModel):

    title: str

    category: str

    summary: str

    keywords: list[str]