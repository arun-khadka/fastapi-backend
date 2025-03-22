from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Test database connection
try:
    with engine.connect() as connection:
        print("Database connected successfully!")
except Exception as error:
    print("Failed to connect to the database.")
    print("Error:", error)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
