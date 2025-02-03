import os
from typing import List

from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker

from utils.database.database_tables import Listing
from models.modes import Mode

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

def get_listing_to_process(limit:int) -> List[Listing]:
    database = SessionLocal()

    try:
        return database.query(Listing).filter(and_(or_(Listing.successful.is_(None), Listing.successful.is_(False)), Listing.mode.__ne__(Mode.RECIPE_LINKS))).limit(limit).all()
    
    finally:
        database.close()

def update_listing(listing:Listing):
    database = SessionLocal()
    
    try:
        database.query(Listing).where(Listing.id == listing.id).update({
            "attempts": listing.attempts, 
            "enddate": listing.enddate,
            "successful": listing.successful,
            "startdate": listing.startdate
        })
        database.commit()
    
    finally:
        database.close()
