from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(10), default="user")  # 'user' or 'admin'

class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), unique=True, nullable=False)
    train_name = Column(String(100), nullable=False)
    train_type = Column(String(10))
    run_days = Column(String(100))  # Comma-separated
    train_origin_station = Column(String(100))
    train_origin_station_code = Column(String(10))
    train_destination_station = Column(String(100))
    train_destination_station_code = Column(String(10))
    depart_time = Column(String(10))
    arrival_time = Column(String(10))
    distance = Column(String(10))
    class_type = Column(String(100))  # Comma-separated
    day_of_journey = Column(Integer)
