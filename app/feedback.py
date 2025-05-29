from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, Table, MetaData
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# ✅ Replace with your actual PostgreSQL connection details
DATABASE_URL = "postgresql://username:password@localhost:5432/your_database"

# Create engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the feedback table
feedback_table = Table(
    "feedback", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("step", Integer),
    Column("type", String),
    Column("amount", Float),
    Column("nameOrig", String),
    Column("oldbalanceOrg", Float),
    Column("newbalanceOrig", Float),
    Column("nameDest", String),
    Column("oldbalanceDest", Float),
    Column("newbalanceDest", Float),
    Column("isFraud", Integer)
)

# Create table if it doesn't exist
metadata.create_all(engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the request schema
class FeedbackInput(BaseModel):
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int

# Endpoint to receive feedback
@app.post("/feedback")
def feedback(feedback: FeedbackInput):
    try:
        db = SessionLocal()
        insert_query = feedback_table.insert().values(**feedback.dict())
        db.execute(insert_query)
        db.commit()
        db.close()
        return {"message": "✅ Feedback saved to PostgreSQL database successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error saving feedback: {e}")
