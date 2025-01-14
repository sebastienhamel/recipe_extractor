from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABSE_URL = os.getenv("DATABASE_URL")

if not DATABSE_URL:
    raise ValueError("DATABASE_URL environment variable cannot be found.")


engine = create_engine(DATABSE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

def get_database():
    database = SessionLocal()

    try:
        yield database
    
    finally:
        database.close()

