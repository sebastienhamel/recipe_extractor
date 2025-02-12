import os
from typing import List

from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker

from src.utils.database.database_tables import Listing
from src.models.modes import Mode

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable cannot be found.")


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

def get_database():
    database = SessionLocal()

    try:
        yield database
    
    finally:
        database.close()

def is_listing_complete():
    database = SessionLocal()

    try:
        return database.query(Listing).filter(
            Listing.mode.__ne__(Mode.RECIPE_LINKS)).count() == database.query(Listing).filter(
            and_(
                Listing.mode.__ne__(Mode.RECIPE_LINKS),
                Listing.successful.__eq__(1)
            )
        ).count() and database.query(Listing).count() > 0
    
    finally:
        database.close()

def is_detail_complete():
    database = SessionLocal()

    try:
        return database.query(Listing).filter(
            and_(
                Listing.mode.__eq__(Mode.RECIPE_LINKS), 
                Listing.successful.__eq__(1)
            ) #number of successful = true == number of recipe links -> The details is complete.
        ).count() == database.query(Listing).filter(
            Listing.mode.__eq__(Mode.RECIPE_LINKS)).count() and database.query(Listing).filter(
                Listing.mode.__eq__(Mode.RECIPE_LINKS)).count() > 0 #There are recipe links present
    finally:
        database.close()

def get_listing_to_process(limit:int) -> List[Listing]:
    database = SessionLocal()

    try:
        return database.query(Listing).filter(and_(or_(Listing.successful.is_(None), Listing.successful.is_(False)), Listing.mode.__ne__(Mode.RECIPE_LINKS))).limit(limit).all()
    
    finally:
        database.close()

def get_details_to_process(limit:int) -> List[Listing]:
    database = SessionLocal()

    try:
        return database.query(Listing).filter(and_(or_(Listing.successful.is_(None), Listing.successful.is_(False)), Listing.mode.__eq__(Mode.RECIPE_LINKS))).limit(limit).all()
    
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
