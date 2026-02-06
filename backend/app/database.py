"""
Database configuration with PostgreSQL support for production.
Handles both SQLite (development) and PostgreSQL (production) connections.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, StaticPool

load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Render uses "postgres://" but SQLAlchemy 2.0 requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def create_database_engine():
    """
    Create SQLAlchemy engine with appropriate settings for SQLite or PostgreSQL.
    """
    if DATABASE_URL.startswith("sqlite"):
        # SQLite configuration (development)
        return create_engine(
            DATABASE_URL,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # Recommended for SQLite
        )
    else:
        # PostgreSQL configuration (production)
        return create_engine(
            DATABASE_URL,
            echo=False,
            future=True,
            # Connection pooling for PostgreSQL
            poolclass=QueuePool,
            pool_size=5,  # Number of permanent connections
            max_overflow=10,  # Additional connections when pool is exhausted
            pool_timeout=30,  # Seconds to wait for a connection
            pool_recycle=1800,  # Recycle connections after 30 minutes
            pool_pre_ping=True,  # Verify connection health before use
        )


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get a database session.
    Properly closes session after request completes.
    """
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Called on application startup.
    """
    Base.metadata.create_all(bind=engine)

