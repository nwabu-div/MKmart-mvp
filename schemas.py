from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User schemas (already there)
class UserCreate(BaseModel):
    phone: Optional[str] = None
    business_name: str
    location: str
    password: str
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    business_name: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
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

# Product schemas (ADD THESE — this na the missing part!)
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity_in_stock: int
    category: str
    subcategory: str

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity_in_stock: int
    category: str
    subcategory: str
    seller_id: int

    class Config:
        from_attributes = True

# Order schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float  # Price at the time of sale (in case price change later)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]  # At least one item

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    seller_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
