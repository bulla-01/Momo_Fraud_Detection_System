#queries.py

from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from database import Feedback, Transaction1  # ORM classes
from models import regtbl
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# -------------- GET Beneficiary ----------------

def get_beneficiary_by_phone(db: Session, phoneno: str):
    all_beneficiaries = db.query(regtbl).all()
    print("All beneficiaries:")
    for b in all_beneficiaries:
        print(b.phone_number)
    return db.query(regtbl).filter(regtbl.phone_number == phoneno).first()
 #-------------- GET Initiator Balance ----------------

def get_initiator_balance_by_phone(db: Session, phone_number: str):
    # Query to get the latest transaction for the initiator
    transaction = db.query(Transaction1).filter(Transaction1.nameOrig == phone_number).order_by(Transaction1.trxdate.desc()).first()
    
    if transaction:
        return transaction.newbalanceOrig  # Return the initiator's previous balance (origin)
    return None
    
#-------------- GET Initiator Location ----------------

def get_initiator_location_by_phone(db: Session, phone_number: str):
    # Query to get the initiator's registration record
    location = db.query(regtbl).filter(regtbl.phone_number == phone_number).first()
    
    if location and location.latitude is not None and location.longitude is not None:
        return location.latitude, location.longitude  # Return as a tuple
    return None



# -------------- CREATE Feedback ----------------
def create_feedback(db: Session, feedback_data: dict):
    insert_stmt = Feedback.__table__.insert().values(**feedback_data)  # Fixed reference to ORM table
    db.execute(insert_stmt)
    db.commit()

# -------------- GET Feedback ----------------
def get_feedback(db: Session, feedback_id: int = None):
    if feedback_id:
        query = select(Feedback).where(Feedback.id == feedback_id)  # Corrected the reference to the ORM model
    else:
        query = select(Feedback)
    result = db.execute(query)
    return result.fetchall()

# -------------- UPDATE Feedback ----------------
def update_feedback(db: Session, feedback_id: int, update_data: dict):
    update_stmt = Feedback.__table__.update().where(Feedback.id == feedback_id).values(**update_data)  # Fixed reference to ORM table
    db.execute(update_stmt)
    db.commit()

# -------------- DELETE Feedback ----------------
def delete_feedback(db: Session, feedback_id: int):
    delete_stmt = Feedback.__table__.delete().where(Feedback.id == feedback_id)  # Fixed reference to ORM table
    db.execute(delete_stmt)
    db.commit()
