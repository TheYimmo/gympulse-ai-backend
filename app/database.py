from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from gympulse.config import get_database_url

Base = declarative_base()
engine = None
SessionLocal = None

db_url = get_database_url()
if db_url:
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    if engine:
        from app.models import GymData  # noqa: F401

        Base.metadata.create_all(bind=engine)


def ping_database() -> bool:
    if not engine:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
