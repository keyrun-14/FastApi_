from sqlalchemy import Column, Integer, Float, String
from database.db import Base

class CityDetail(Base):
    __tablename__ = "CityDetails"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    state = Column(String)
    pincode = Column(Integer)
    longitude = Column(Float)
    latitude = Column(Float)