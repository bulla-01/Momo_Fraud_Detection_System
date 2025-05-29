# models
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Numeric, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import JSON


# SQLAlchemy base
Base = declarative_base()
# ---------- ORM MODELS ----------

class regtbl(Base):
    __tablename__ = "regtbl"

    phone_number = Column(String, primary_key=True, nullable=False)
    fullname = Column(String)
    date_of_birth = Column(Date)
    email = Column(String)
    house_address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    id_number = Column(String)
    tin = Column(String)
    next_of_kin = Column(String)
    next_of_kin_phone = Column(String)
    pin = Column(String(4))

class PredictionAnalysis(Base):
    __tablename__ = "prediction_analysis"

    id = Column(Integer, primary_key=True, index=True)
    step = Column(Integer)
    type = Column(String(50))
    amount = Column(Float)
    nameorig = Column(String(100))
    oldbalanceorg = Column(Float)
    newbalanceorig = Column(Float)
    namedest = Column(String(100))
    oldbalancedest = Column(Float)
    newbalancedest = Column(Float)
    trxdate = Column(DateTime)
    beneficiaryname = Column(String(100))
    mobilenetwork = Column(String(50))
    is_fraud = Column(Boolean)
    fraud_probability = Column(Float)
    prediction_label = Column(String(255))
    prediction_description = Column(String(50))
    prediction_date = Column(DateTime, default=datetime.utcnow)

    # ✅ Add these fields
    latitude = Column(Float)
    longitude = Column(Float)


    # Normalized prediction fields
    is_fraud = Column(Boolean)
    fraud_probability = Column(Float)
    prediction_label = Column(String(255))
    prediction_description = Column(String(50))
    prediction_date = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    step = Column(Integer)
    type = Column(String(50))
    amount = Column(Float)
    nameOrig = Column(String(255))
    oldbalanceOrg = Column(Float)
    newbalanceOrig = Column(Float)
    nameDest = Column(String(255))
    oldbalanceDest = Column(Float)
    newbalanceDest = Column(Float)
    isFraud = Column(Integer)


class Transaction1(Base):
    __tablename__ = "transactiontbl"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    trxdate = Column(DateTime, nullable=False)
    step = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    nameOrig = Column(String(255), nullable=False)
    oldbalanceOrg = Column(Numeric(12, 2))
    newbalanceOrig = Column(Numeric(12, 2))
    nameDest = Column(String(255), nullable=False)
    oldbalanceDest = Column(Numeric(12, 2))
    newbalanceDest = Column(Numeric(12, 2))
    mobilenetwork = Column(String(50), nullable=True)
    beneficiaryname = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Transaction1(id={self.id}, type='{self.type}', amount={self.amount})>"


# ---------- Pydantic INPUT MODEL ----------

class TransactionData(BaseModel):
    trxdate: datetime
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    mobilenetwork: str

    class Config:
        orm_mode = True
