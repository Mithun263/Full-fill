import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/acme_db")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:1234@localhost:5432/acme_db")

# Async engine for FastAPI (used in routes)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # turn off SQL logs for speed
    pool_size=10,
    max_overflow=20,
    future=True
)

# Sync engine for Celery or batch tasks
sync_engine = create_engine(
    DATABASE_URL_SYNC,
    echo=False,
    pool_size=10,
    max_overflow=20,
    future=True
)

# Session factories
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()
