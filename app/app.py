from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging
import json
# Routers and local modules
from routers import feedback, status, transaction
from routers.initiator import router as initiator_router
import regtb
import validate_initiator
import initiator_location
from database import get_db
from predict import preprocess_input, predict_fraud, send_fraud_alert_email
from analysis_fastapi import save_prediction_to_db
import analysis_fastapi

# FastAPI App Setup
app = FastAPI(
    title="📈 MOMO Fraud Detection API",
    version="1.0",
    description="Fraud prediction using MLP + XGBoost + Random Forest ensemble."
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/app_logs.log"),
        logging.StreamHandler()
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic Schema
class TransactionInput(BaseModel):
    trxdate: str
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    beneficiaryname: str
    oldbalanceDest: float
    newbalanceDest: float
    mobilenetwork: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ✅ Prediction Endpoint
@app.post("/predict")
def predict(txn: TransactionInput, db: Session = Depends(get_db)):
    try:
        txn_data = txn.dict()
        logging.info(f"📦 Incoming transaction data: {json.dumps(txn_data, indent=2)}")

        # Make prediction
        is_fraud, risk_score, reason, detail = predict_fraud(txn_data)
        description = "Fraud" if is_fraud == 1 else "Legitimate"
        prediction_date = datetime.utcnow()

        # Send alert if fraudulent
        if is_fraud == 1:
            logging.info("Fraud detected. Attempting to send alert email...")
            send_fraud_alert_email(txn_data, is_fraud, risk_score, reason)

        # Save prediction
        save_prediction_to_db(
            db=db,
            transaction=txn,
            is_fraud=is_fraud,
            fraud_prob=risk_score,
            label=reason,
            description=description
        )

        return {
            "is_fraud": is_fraud,
            "risk_score": risk_score,
            "reason": reason,
            "detail": detail,
            "prediction": description
        }

    except Exception as e:
        logging.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Fraud Detection API"}

# ✅ Register all routers
app.include_router(transaction.router)
app.include_router(feedback.router)
app.include_router(status.router)
app.include_router(initiator_router)
app.include_router(validate_initiator.router)
app.include_router(regtb.router, prefix="/reg")
app.include_router(initiator_location.router)
app.include_router(analysis_fastapi.router)
