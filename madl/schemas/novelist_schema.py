from datetime import datetime

from pydantic import BaseModel


class NovelistSchema(BaseModel):
    name: str


class NovelistPublicSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class PaginatedNovelistsResponse(BaseModel):
    novelists: list[NovelistPublicSchema]
    total: int
    page: int
    per_page: int
    total_pages: int


class NovelistUpdateSchema(BaseModel):
    name: str | None = None
