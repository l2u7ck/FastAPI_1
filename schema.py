from pydantic import BaseModel, ConfigDict
from datetime import date


class ItemAnnCreate(BaseModel):
    title: str
    description: str | None = None
    cost: float
    owner: str

class AnnouncementSchema(BaseModel):
    title: str
    description: str | None
    cost: float
    owner: str
    create_date: date | None

    # Активируем поддержку ORM-конвертации
    model_config = ConfigDict(from_attributes=True)


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
