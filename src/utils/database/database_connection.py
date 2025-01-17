import os

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from utils.database.database_tables import Listing

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

def get_listing_to_process(limit:int):
    database = SessionLocal()

    try:
       return database.query(Listing).filter(or_(Listing.successful.is_(None), Listing.successful.is_(False))).limit(limit).all()
    
    finally:
        database.close()
