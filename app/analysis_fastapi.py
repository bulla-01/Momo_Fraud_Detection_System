#analysis_fastapi.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Transaction1, PredictionAnalysis
from analysis_schema import TransactionInput
from predict import predict_fraud, send_fraud_alert_email
import logging

router = APIRouter()

def insert_transaction_to_db(db: Session, transaction: TransactionInput):
    trx = Transaction1(
        trxdate=datetime.fromisoformat(transaction.trxdate.replace("Z", "+00:00")),
        step=transaction.step,
        type=transaction.type,
        amount=transaction.amount,
        nameOrig=transaction.nameOrig,
        oldbalanceOrg=transaction.oldbalanceOrg,
        newbalanceOrig=transaction.newbalanceOrig,
        nameDest=transaction.nameDest,
        oldbalanceDest=transaction.oldbalanceDest,
        newbalanceDest=transaction.newbalanceDest,
        mobilenetwork=transaction.mobilenetwork,
        beneficiaryname=transaction.beneficiaryname,
    )
    db.add(trx)
    db.commit()
    db.refresh(trx)
    return trx

logging.info("✅ Correct save_prediction_to_db function is being called")

def save_prediction_to_db(
    db: Session,
    transaction: TransactionInput,
    is_fraud: bool,
    fraud_prob: float,
    label: str,
    description: str
):
    now = datetime.utcnow()

    record = PredictionAnalysis(
        step=transaction.step,
        type=transaction.type,
        amount=transaction.amount,
        nameorig=transaction.nameOrig,
        oldbalanceorg=transaction.oldbalanceOrg,
        newbalanceorig=transaction.newbalanceOrig,
        namedest=transaction.nameDest,
        oldbalancedest=transaction.oldbalanceDest,
        newbalancedest=transaction.newbalanceDest,
        trxdate=now,
        beneficiaryname=transaction.beneficiaryname,
        mobilenetwork=transaction.mobilenetwork,
        is_fraud=is_fraud,
        fraud_probability=fraud_prob,
        prediction_label=label,
        prediction_description=description,
        prediction_date=now
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record



@router.post("/predict")
def predict_and_log(transaction: TransactionInput, db: Session = Depends(get_db)):
    try:
        # Run prediction
        is_fraud, fraud_prob, label, description = predict_fraud(transaction.dict())

        # Insert into transaction table
        insert_transaction_to_db(db, transaction)

        # Save and alert only if fraudulent
        saved = None
        if is_fraud:
            send_fraud_alert_email(transaction.dict(), is_fraud, fraud_prob, description)
            saved = save_prediction_to_db(db, transaction, is_fraud, fraud_prob, label, description)

        return {
            "status": "success",
            "is_fraud": is_fraud,
            "probability": fraud_prob,
            "label": label,
            "description": description,
            "prediction_id": saved.id if saved else None
        }

    except Exception as e:
        logging.error(f"❌ Error in prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
