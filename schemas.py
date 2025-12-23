from pydantic import BaseModel
from typing import Optional

# For creating new user
class UserCreate(BaseModel):
    phone: str
    business_name: str
    location: str
    password: str

#For creating nice JSON format the server would send out back to the client/user
class UserOut(BaseModel):
    id: int
    phone: str
    business_name: str
    location: str

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy model to Pydantic

# For creating product
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity_in_stock: int
    category: str
    subcategory: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    quantity_in_stock: int
    category: str
    subcategory: Optional[str]
    seller_id: int

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str