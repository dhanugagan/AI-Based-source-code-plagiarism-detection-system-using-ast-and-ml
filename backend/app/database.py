"""
SQLAlchemy engine, session factory, and declarative base.

NOTE ON DATABASE CHOICE: the original spec calls for MySQL. This reference
implementation defaults to SQLite (zero external setup, works out of the box)
via DATABASE_URL. To use MySQL instead, set:
    DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
and add `PyMySQL` to requirements.txt (already listed as optional). The
SQLAlchemy models are portable between both engines without changes.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models so they register with Base.metadata before create_all
    from app.models import user, submission, comparison, report  # noqa: F401
    Base.metadata.create_all(bind=engine)
