from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@172.17.0.1:5432/product_engine"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def create_db_session() -> Session:
    db_session: Session = SessionMaker()
    try:
        yield db_session
    finally:
        db_session.close()
