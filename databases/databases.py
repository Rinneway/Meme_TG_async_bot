import os
import sys
import logging
from typing import Optional, List, Dict

# Добавляем корень проекта в sys.path (для импорта constants)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = str(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from .models import Base, Category, Keyword, Subreddit
from constants import MEME_KEYWORDS, TOPIC_NAMES, SUBREDDITS

logger = logging.getLogger(__name__)

# Для локальной разработки — файл, для Vercel — in-memory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Создаёт таблицы и заполняет начальными данными."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        result = await session.execute(select(func.count(Category.id)))
        count = result.scalar()

        if count == 0:
            logger.info("Database is empty, seeding initial data from constants.py...")
            await seed_initial_data(session)
            await session.commit()

    logger.info("Database initialized successfully")


async def seed_initial_data(session: AsyncSession):
    """Заполняет БД данными из constants.py."""
    categories_data = []

    for category_name in MEME_KEYWORDS:
        categories_data.append({
            "name": category_name,
            "display_name": TOPIC_NAMES.get(category_name, category_name),
            "keywords": MEME_KEYWORDS[category_name],
            "subreddits": SUBREDDITS.get(category_name, [])
        })

    for cat_data in categories_data:
        category = Category(
            name=cat_data["name"],
            display_name=cat_data["display_name"]
        )
        session.add(category)
        await session.flush()

        for keyword in cat_data["keywords"]:
            session.add(Keyword(category_id=category.id, keyword=keyword))

        for subreddit in cat_data["subreddits"]:
            session.add(Subreddit(category_id=category.id, name=subreddit))

    await session.commit()
    logger.info(f"Seeded {len(categories_data)} categories from constants.py")


async def find_category_by_text(_text: str) -> Optional[Dict]:
    """Ищет категорию по тексту сообщения."""
    text_lower = _text.lower()

    async with async_session_maker() as session:
        query = (
            select(Category)
            .join(Keyword, Category.id == Keyword.category_id)
            .where(
                Category.is_active == True,
                literal(text_lower).like(f"%{Keyword.keyword}%")
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
    """Добавляет новую категорию."""
    try:
        async with async_session_maker() as session:
            existing = await session.execute(
                select(Category).where(Category.name == name)
            )
            if existing.scalar_one_or_none():
                logger.warning(f"Category '{name}' already exists")
                return False

            category = Category(name=name, display_name=display_name)
            session.add(category)
            await session.flush()

            for keyword in keywords:
                session.add(Keyword(category_id=category.id, keyword=keyword))

            for subreddit in subreddits:
                session.add(Subreddit(category_id=category.id, name=subreddit))

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        return False


async def delete_category(name: str) -> bool:
    """Помечает категорию как неактивную."""
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