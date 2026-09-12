from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class AgentResponse(BaseModel):

    answer: str

    tool_used: str | None = None

    tool_result: dict[str, Any] | None = None


class CalculatorArgs(BaseModel):

    expression: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )


class WeatherArgs(BaseModel):

    city: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


class SearchArgs(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )


class DatabaseQueryArgs(BaseModel):

    department: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )