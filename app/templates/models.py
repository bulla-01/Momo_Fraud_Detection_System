from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RiskUser(BaseModel):
    id: int
    namedest: str
    fraud_probability: float
    
    class Config:
        orm_mode = True  # Allows compatibility with SQLAlchemy ORM

class RiskUserResponse(BaseModel):
    users: List[RiskUser]

