import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Integer, Date, func, Float

load_dotenv()
# Параметры подключения к базе данных
db_params = {

    'user': os.getenv('DB_USER'),
    'password': os.getenv('PASSWORD'),
    'host': os.getenv('DB_HOST', "localhost"),  # Или адрес вашего сервера БД
    'port': os.getenv('DB_PORT', "5432"),
    'dbname': os.getenv('DB_NAME')
}
POSTGRES_DNS = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}".format(**db_params)
engine = create_async_engine(POSTGRES_DNS)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with Session() as session:
        try:
            yield session
        finally:
            await session.close()


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Announcement(Base):
    __tablename__ = "Announcement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    cost: Mapped[float] = mapped_column(Float)
    owner: Mapped[str] = mapped_column(String)
    create_date: Mapped[datetime.date] = mapped_column(
        Date,
        server_default=func.now()
    )

    @property
    def dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cost": self.cost,
            "owner": self.owner,
            "create_date": self.create_date.isoformat(),
        }


async def init_orm(drop_existing=True):
    try:
        async with engine.begin() as conn:
            if drop_existing:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Ошибка соединения с базой данных: {e}")


async def close_orm():
    await engine.dispose()


