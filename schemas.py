from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    phone: Optional[str] = None
    business_name: str
    location: str
    password: str
    email: str

class UserLogin(BaseModel):
    email: str  # Now login with email
    password: str

class UserOut(BaseModel):
    id: int
    phone: Optional[str]
    business_name: str
    location: str
    email: str
    is_verified: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ... rest of product and order schemas remain the same