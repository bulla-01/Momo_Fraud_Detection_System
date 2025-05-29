# initiator_location.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from queries import get_initiator_location_by_phone
from database import get_db
from schemas import BeneficiaryResponse
from models import Transaction1, regtbl

router = APIRouter()

@router.get("/initiator_location/{phone_number}")
def initiator_location(phone_number: str, db: Session = Depends(get_db)):
    location = db.query(regtbl).filter(regtbl.phone_number == phone_number).first()

    if location and location.latitude is not None and location.longitude is not None:
        loc = get_initiator_location_by_phone(db, phone_number)
        return {
    "success": True,
    "latitude": location.latitude,
    "longitude": location.longitude
}
    else:
        return {"success": False, "message": "Initiator's location not found"}
        

