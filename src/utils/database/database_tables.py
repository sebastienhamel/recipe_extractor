from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()

class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key = True, autoincrement = True)
    link = Column(String(255), unique = True, nullable = False)
    mode = Column(String(255), nullable = False)
    startdate = Column(DateTime, nullable = True)
    enddate = Column(DateTime, nullable = True)
    successful = Column(Boolean, nullable = True)
    attempts = Column(Integer, nullable = True)


# class DetailTable(Base):
#     __tablename__ = "details"
#     id = Column(Integer, primary_key = True, autoincrement = True)
#     link = Column(String, unique = True, nullable = False)
#     startdate = Column(DateTime, nullable = True)
#     enddate = Column(DateTime, nullable = True)
#     successful = Column(Boolean, nullable = True)
#     attempts = Column(Integer, nullable = True)
#     data = Column(JSON, nullable = True)


    