from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from migrate_db import Announcement, init_orm, close_orm, get_session
from schema import ItemAnnUpdate, ItemAnnCreate, ItemAnnSearchParams


@asynccontextmanager
async def orm_context(app: FastAPI):
    print("Start")
    await init_orm()
    try:
        yield
    finally:
        await close_orm()
        print("Finish")

app = FastAPI(lifespan=orm_context)


@app.post('/announcement', tags=['todo'], response_model=dict)
async def create_ann(todo: ItemAnnCreate, session: AsyncSession = Depends(get_session)):  # Зависимость сессии
    try:
        session.add(Announcement(**dict(todo)))
        await session.commit()
    except Exception as ex:
        return {"status": "error", "message": f"Ошибка: {str(ex)}"}
    return {"status": "ok", "data": todo.dict()}


@app.patch('/announcement/{ann_id}', tags=['todo'], response_model=dict)
async def search_id(ann_id: int, update_data: ItemAnnUpdate, session: AsyncSession = Depends(get_session)):
    try:
        ann = await session.get(Announcement, ann_id)
        if ann is None:
            raise HTTPException(status_code=404, detail=f"Запись с ID={ann_id} не найдена.")

        # Частичное обновление полей
        update_values = update_data.model_dump(exclude_unset=True)
        for attr, value in update_values.items():
            setattr(ann, attr, value)

        # Сохраняем изменения
        await session.commit()
        await session.refresh(ann)
        return {"status": "ok", "data": ann.dict}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении объявления: {ex}")


@app.delete('/announcement/{ann_id}', response_model=dict)
async def delete_ann(ann_id: int, session: AsyncSession = Depends(get_session)):
    try:
        ann = await session.get(Announcement, ann_id)
        if ann is None:
            raise HTTPException(status_code=404, detail=f"Запись с ID={ann_id} не найдена.")

        # Удаление объявления
        await session.delete(ann)
        await session.commit()
    except Exception as ex:
        return {"status": "error", "message": f"Ошибка: {str(ex)}"}
    return {"status": "ok", "data": ann.dict}


@app.get('/announcement/{ann_id}', response_model=dict)
async def search_id(ann_id: int, session: AsyncSession = Depends(get_session)):
    try:
        ann = await session.get(Announcement, ann_id)
        if ann is None:
            raise HTTPException(status_code=404, detail=f"Запись с ID={ann_id} не найдена.")
    except Exception as ex:
        return {"status": "error", "message": f"Ошибка: {str(ex)}"}
    return {"status": "ok", "data": ann.dict}


@app.get('/announcement', response_model=dict)
async def search_params(params: ItemAnnSearchParams = Depends(), session: AsyncSession = Depends(get_session)):
    try:
        # Проверяем, что хотя бы один параметр задан
        if not any(vars(params).values()):
            raise HTTPException(status_code=400, detail="Требуется хотя бы один параметр для поиска.")

        # Создаем запрос
        query = select(Announcement)

        # Строим фильтры
        filters = []
        if params.title:
            filters.append(Announcement.title.ilike(f"%{params.title}%"))
        if params.description:
            filters.append(Announcement.description.ilike(f"%{params.description}%"))
        if params.cost:
            filters.append(Announcement.cost == params.cost)
        if params.owner:
            filters.append(Announcement.owner == params.owner)
        if params.create_date:
            # Парсим дату из строки
            create_date = datetime.strptime(params.create_date, "%Y-%m-%d").date()
            filters.append(Announcement.create_date == create_date)

        # Добавляем фильтры в запрос
        if filters:
            query = query.where(and_(*filters))

        # Выполняем запрос
        result = await session.execute(query)
        adverts = [res.dict for res in result.scalars().all()]

        if adverts is None:
            raise HTTPException(status_code=404, detail=f"Записей с данными параметрами нет.")
    except Exception as ex:
        return {"status": "error", "message": f"Ошибка: {str(ex)}"}
    return {"status": "ok", "data": adverts}
