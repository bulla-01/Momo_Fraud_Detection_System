#validate_initiator.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from queries import get_initiator_balance_by_phone
from database import get_db
from models import Transaction1
#from models import regtbl

router = APIRouter()

@router.get("/validate_initiator/{phone_number}")
def validate_initiator(phone_number: str, db: Session = Depends(get_db)):
    initiator = db.query(Transaction1).filter(Transaction1.nameOrig == phone_number).first()

    if initiator:
        balance = get_initiator_balance_by_phone(db, phone_number)
        return {
            "success": True,
            "balance": float(balance) if balance is not None else 0.0
        }
    else:
        return {
            "success": False,
            "message": "Initiator not found"
        }


