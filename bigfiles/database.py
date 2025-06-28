from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from bigfiles import config

print(config.DATABASE_PATH)
db = create_engine(config.DATABASE_PATH)
SessionLocal = sessionmaker(bind=db, autoflush=False, autocommit=False)
session = SessionLocal()
Base = declarative_base()


def iniciar_db():
    Base.metadata.create_all(db)

