import json
import os
import logging
from typing import Optional, List, Dict
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from models import Base, Category, Keyword, Subreddit

logger = logging.getLogger(__name__)

# Для Vercel используем SQLite in-memory, для локальной разработки — файл
# Можно легко переключить на PostgreSQL: postgresql+asyncpg://user:pass@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

# Создаём движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True для отладки SQL-запросов
    future=True
)

# Создаём фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Создаёт таблицы и заполняет начальными данными."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Проверяем, есть ли данные
    async with async_session_maker() as session:
        result = await session.execute(select(func.count(Category.id)))
        count = result.scalar()

        if count == 0:
            logger.info("Database is empty, seeding initial data...")
            await seed_initial_data(session)
            await session.commit()

    logger.info("Database initialized successfully")


async def seed_initial_data(session: AsyncSession):
    """Заполняет БД начальными данными из JSON."""
    json_path = os.path.join(str(os.path.dirname(__file__)), "categories.json")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for category_data in data["categories"]:
        # Создаём категорию
        category = Category(
            name=category_data["name"],
            display_name=category_data["display_name"]
        )
        session.add(category)
        await session.flush()  # Получаем ID категории

        # Добавляем ключевые слова
        for keyword in category_data["keywords"]:
            session.add(Keyword(category_id=category.id, keyword=keyword))

        # Добавляем сабреддиты
        for subreddit in category_data["subreddits"]:
            session.add(Subreddit(category_id=category.id, name=subreddit))

    await session.commit()
    logger.info("Initial data seeded successfully")


async def find_category_by_text(_text: str) -> Optional[Dict]:
    """
    Ищет категорию по тексту сообщения.
    Возвращает dict с данными или None.
    """
    text_lower = _text.lower()

    async with async_session_maker() as session:
        # Ищем совпадение по ключевому слову (LIKE для частичного совпадения)
        # Сортируем по длине ключа (более длинные = более точные)
        query = (
            select(Category)
            .join(Keyword, Category.id == Keyword.category_id)
            .where(
                Category.is_active == True,
                text.like(f"%{Keyword.keyword}%")
            )
            .order_by(func.length(Keyword.keyword).desc())
            .limit(1)
            .options(selectinload(Category.subreddits))
        )

        result = await session.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            return None

        return {
            "id": category.id,
            "name": category.name,
            "display_name": category.display_name,
            "subreddits": [sub.name for sub in category.subreddits]
        }


async def get_all_active_categories() -> List[Dict]:
    """Возвращает все активные категории."""
    async with async_session_maker() as session:
        query = select(Category).where(Category.is_active == True)
        result = await session.execute(query)
        categories = result.scalars().all()

        return [
            {"name": cat.name, "display_name": cat.display_name}
            for cat in categories
        ]


async def add_category(
        name: str,
        display_name: str,
        keywords: List[str],
        subreddits: List[str]
) -> bool:
    """Добавляет новую категорию. Возвращает True при успехе."""
    try:
        async with async_session_maker() as session:
            # Проверяем уникальность имени
            existing = await session.execute(
                select(Category).where(Category.name == name)
            )
            if existing.scalar_one_or_none():
                logger.warning(f"Category '{name}' already exists")
                return False

            # Создаём категорию
            category = Category(name=name, display_name=display_name)
            session.add(category)
            await session.flush()

            # Добавляем ключевые слова
            for keyword in keywords:
                session.add(Keyword(category_id=category.id, keyword=keyword))

            # Добавляем сабреддиты
            for subreddit in subreddits:
                session.add(Subreddit(category_id=category.id, name=subreddit))

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        return False


async def delete_category(name: str) -> bool:
    """Помечает категорию как неактивную (мягкое удаление)."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(Category).where(Category.name == name)
        )
        category = result.scalar_one_or_none()

        if not category:
            return False

        category.is_active = False
        await session.commit()
        return True


async def get_category_stats() -> Dict:
    """Возвращает статистику по БД."""
    async with async_session_maker() as session:
        categories_count = await session.execute(
            select(func.count(Category.id)).where(Category.is_active == True)
        )
        keywords_count = await session.execute(
            select(func.count(Keyword.id))
        )
        subreddits_count = await session.execute(
            select(func.count(Subreddit.id))
        )

        return {
            "categories": categories_count.scalar(),
            "keywords": keywords_count.scalar(),
            "subreddits": subreddits_count.scalar()
        }