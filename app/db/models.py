from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    chunking_strategy = Column(String)
    embedding_model = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InterviewBooking(Base):
    __tablename__ = "interview_bookings"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String)
    booking_date = Column(String)
    booking_time = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())