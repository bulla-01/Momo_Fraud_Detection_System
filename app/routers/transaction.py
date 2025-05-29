from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction1, PredictionAnalysis
from predict import predict_fraud
from datetime import datetime, timezone
import logging

router = APIRouter()

# ---------- Pydantic Input Model ----------
class TransactionData(BaseModel):
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

# ---------- Database Save Function ----------
# def save_prediction_to_db(
    # db: Session,
    # step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    # nameDest, oldbalanceDest, newbalanceDest, trxdate, beneficiaryname,
    # mobilenetwork, is_fraud, risk_score, reason,
    # prediction_description, prediction_date
# ):
    # try:
        # new_record = PredictionAnalysis(
            # step=step,
            # type=type,
            # amount=amount,
            # nameorig=nameOrig,
            # oldbalanceorg=oldbalanceOrg,
            # newbalanceorig=newbalanceOrig,
            # namedest=nameDest,
            # oldbalancedest=oldbalanceDest,
            # newbalancedest=newbalanceDest,
            # trxdate=trxdate,
            # beneficiaryname=beneficiaryname,
            # mobilenetwork=mobilenetwork,
            # is_fraud=is_fraud,
            # risk_score=risk_score,
            # reason=reason,
            # prediction_description=prediction_description,
            # prediction_date=prediction_date
        # )
        # db.add(new_record)
        # db.commit()
        # logging.info("✅ Prediction saved successfully.")

    # except Exception as e:
        # db.rollback()
        # logging.error(f"[X] Error saving prediction data: {e}")
        # raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

# ---------- API Endpoint ----------
@router.post("/transactions/submit", operation_id="submit_transaction")
async def submit_transaction(transaction: TransactionData, db: Session = Depends(get_db)):
    try:
        now = datetime.now(timezone.utc)

        transaction_record = Transaction1(
            trxdate=now,
            step=transaction.step,
            type=transaction.type,
            amount=transaction.amount,
            nameOrig=transaction.nameOrig,
            oldbalanceOrg=transaction.oldbalanceOrg,
            newbalanceOrig=transaction.newbalanceOrig,
            nameDest=transaction.nameDest,
            beneficiaryname=transaction.beneficiaryname,
            oldbalanceDest=transaction.oldbalanceDest,
            newbalanceDest=transaction.newbalanceDest,
            mobilenetwork=transaction.mobilenetwork
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        return {"message": "Transaction submitted successfully", "id": transaction_record.id}

    except Exception as e:
        import logging
        logging.error(f"Transaction failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction submission failed.")
