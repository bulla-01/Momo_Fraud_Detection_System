# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Feedback, Transaction1  #Transaction, Import Base and models
from sqlalchemy.ext.declarative import declarative_base
# Database URL and Engine
DATABASE_URL = "postgresql://postgres:Bentjun25%24@localhost:5432/momo_db"
engine = create_engine(DATABASE_URL)

# SessionLocal: to create sessions in your API endpoints
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the tables in the database (if needed)
def init_db():
    Base.metadata.create_all(bind=engine)
