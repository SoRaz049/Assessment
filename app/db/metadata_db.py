from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models import Base

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