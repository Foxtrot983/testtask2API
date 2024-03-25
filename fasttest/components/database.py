from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

from sqlalchemy_utils import database_exists, create_database

from .config import DATABASE


class Base(DeclarativeBase):
    pass

engine = create_engine(URL.create(**DATABASE))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


if not database_exists(engine.url):
    create_database(engine.url)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
