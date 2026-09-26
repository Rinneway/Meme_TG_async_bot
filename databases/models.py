from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)

    # Связи
    keywords = relationship("Keyword", back_populates="category", cascade="all, delete-orphan")
    subreddits = relationship("Subreddit", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(name='{self.name}', display='{self.display_name}')>"


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    keyword = Column(String(100), nullable=False, index=True)

    # Связь
    category = relationship("Category", back_populates="keywords")

    def __repr__(self):
        return f"<Keyword(keyword='{self.keyword}')>"


class Subreddit(Base):
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)

    # Связь
    category = relationship("Category", back_populates="subreddits")

    def __repr__(self):
        return f"<Subreddit(name='{self.name}')>"