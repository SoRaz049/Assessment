from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.db.models import Base

from .models import FileMetadata, InterviewBooking

# Create the engine to connect to the database
engine = create_engine(settings.DATABASE_URL)

# SessionLocal class is a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # This creates all the tables defined in models.py
    Base.metadata.create_all(bind=engine)

def get_db():
    # Dependency to get a DB session for each request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def save_file_metadata(db: Session, file_name: str, chunking_strategy: str, embedding_model: str):
    """Saves a record of the processed file to the PostgreSQL database."""
    db_file = FileMetadata(
        file_name=file_name,
        chunking_strategy=chunking_strategy,
        embedding_model=embedding_model,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def save_booking(db: Session, full_name: str, email: str, date: str, time: str) -> int:
    """Saves an interview booking to the PostgreSQL database."""
    booking = InterviewBooking(
        full_name=full_name, 
        email=email, 
        booking_date=date, 
        booking_time=time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    print(f"Successfully saved booking for {full_name} with ID {booking.id} to database.")
    return booking.id