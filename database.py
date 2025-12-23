from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file (for secrets later, like DATABASE_URL)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mokomarket.db")
# If you set DATABASE_URL in .env, e go use am. Otherwise, use local SQLite file called mokomarket.db

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# Create the database engine. The connect_args na for SQLite on Windows (avoid threading error)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a factory for database sessions (so we fit open/close connection safely)

Base = declarative_base()
# This Base na the parent class all our models go inherit from

def get_db():
    db = SessionLocal()
    try:
        yield db  # Give the db session to the endpoint
    finally:
        db.close()