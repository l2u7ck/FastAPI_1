from datetime import date

from fastapi import Query
from pydantic import BaseModel


class ItemAnnCreate(BaseModel):
    title: str
    description: str | None = None
    cost: float
    owner: str


class ItemAnnUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    cost: float | None = None


class ItemAnnSearchParams(BaseModel):
    title: str | None = None
    description: str | None = None
    cost: float | None = None
    owner: str | None = None
    create_date: str | None = None
