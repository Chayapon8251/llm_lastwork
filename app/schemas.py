from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    query: str = Field(min_length=1, max_length=300)
    top_k: int = Field(default=3, ge=1, le=5)

    @field_validator("query")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()


class InventoryArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    category: Literal["camera", "audio", "tripod", "lighting"] | None = None
    code: str | None = Field(default=None, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    status: Literal["available", "borrowed", "maintenance"] | None = None


class GroundedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: str = Field(min_length=1, max_length=6000)
    source_ids: list[str] = Field(max_length=10)
    supported: bool


class HistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(max_length=3000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=1000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=12)
    mode: Literal["auto", "demo", "live"] = "auto"

    @field_validator("message")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("message must not be blank")
        return value.strip()
