"""
Database configuration and session management for ACL Guardian.
Supports both SQLite (local dev) and PostgreSQL (production on Render).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./acl_guardian.db")

# Render provides DATABASE_URL with postgres://, but SQLAlchemy needs postgresql://
# Fix the URL if it starts with postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine based on database type
if "postgresql" in DATABASE_URL:
    # PostgreSQL settings for Render
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
        echo=False  # Set to True for SQL query logging
    )
    print("✅ Using PostgreSQL database (Production)")
else:
    # SQLite settings for local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    print("✅ Using SQLite database (Local Development)")

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
