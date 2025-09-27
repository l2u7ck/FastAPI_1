from contextlib import asynccontextmanager
from typing import List
from datetime import date

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from migrate_db import Announcement, init_orm, close_orm, get_session
from schema import ItemAnnCreate, ItemAnnUpdate, AnnouncementSchema


@asynccontextmanager
async def orm_context(app: FastAPI):
    print("Starting ORM...")
    await init_orm()
    try:
        yield
    finally:
        await close_orm()
        print("Closing ORM...")

app = FastAPI(lifespan=orm_context)


# Создание нового объявления
@app.post('/advertisement', tags=['create'])
async def create_ann(todo: ItemAnnCreate, session: AsyncSession = Depends(get_session)):
    new_ann = Announcement(**todo.model_dump())
    session.add(new_ann)
    await session.commit()
    return new_ann


# Обновление существующего объявления
@app.patch('/advertisement/{ann_id}', tags=['update'])
async def update_ann(ann_id: int, update_data: ItemAnnUpdate, session: AsyncSession = Depends(get_session)):
    ann = await session.get(Announcement, ann_id)
    if ann is None:
        raise HTTPException(status_code=404, detail=f"Объявление с ID={ann_id} не найдено.")

    # Применяем частичные обновления
    update_values = update_data.model_dump(exclude_unset=True)
    for attr, value in update_values.items():
        setattr(ann, attr, value)

    await session.commit()
    await session.refresh(ann)
    return ann


# Удаление объявления
@app.delete('/advertisement/{ann_id}', tags=['delete'])
async def delete_ann(ann_id: int, session: AsyncSession = Depends(get_session)):
    ann = await session.get(Announcement, ann_id)
    if ann is None:
        raise HTTPException(status_code=404, detail=f"Объявление с ID={ann_id} не найдено.")

    await session.delete(ann)
    await session.commit()
    return {"detail": "Удалено успешно."}


# Получение конкретного объявления по id
@app.get('/advertisement/{ann_id}', tags=['read'])
async def get_ann_by_id(ann_id: int, session: AsyncSession = Depends(get_session)):
    ann = await session.get(Announcement, ann_id)
    if ann is None:
        raise HTTPException(status_code=404, detail=f"Объявление с ID={ann_id} не найдено.")
    return ann


# Поиск объявлений по параметрам
@app.get('/advertisement', tags=['search'], response_model=List[AnnouncementSchema])
async def search_advertisements(
    title: str | None = Query(None, alias='title'),
    description: str | None = Query(None, alias='description'),
    min_cost: float | None = Query(None, ge=0, le=1000000, alias='minCost'),
    max_cost: float | None = Query(None, ge=0, le=1000000, alias='maxCost'),
    owner: str | None = Query(None, alias='owner'),
    create_date: date | None = Query(None, alias='createDate'),
    session: AsyncSession = Depends(get_session),
):
    """
    Фильтрует объявления по указанным критериям.
    """
    if all(x is None for x in [title, description, min_cost, max_cost, owner, create_date]):
        raise HTTPException(status_code=400, detail="Требуется хотя бы один параметр для поиска.")

    query = select(Announcement)
    filters = []

    if title:
        filters.append(Announcement.title.ilike(f"%{title}%"))
    if description:
        filters.append(Announcement.description.ilike(f"%{description}%"))
    if min_cost is not None:
        filters.append(Announcement.cost >= min_cost)
    if max_cost is not None:
        filters.append(Announcement.cost <= max_cost)
    if owner:
        filters.append(Announcement.owner == owner)
    if create_date:
        filters.append(Announcement.create_date == create_date)

    if filters:
        query = query.where(and_(*filters))

    results = await session.execute(query)
    adverts = results.scalars().all()
    if not adverts:
        raise HTTPException(status_code=404, detail="Ничего не найдено.")

    # Преобразуем объекты SQLAlchemy в объекты Pydantic
    return [AnnouncementSchema.from_orm(ad) for ad in adverts]