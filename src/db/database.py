# src/db/database.py
from sqlmodel import create_engine, SQLModel, Session
from src.core.config import settings

# The database_url from our config file
engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables():
    # This function creates the tables based on our models
    SQLModel.metadata.create_all(engine)

def get_session():
    # This will be used by FastAPI to get a database session for each request
    with Session(engine) as session:
        yield session