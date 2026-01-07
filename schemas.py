from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    phone: Optional[str] = None
    business_name: str
    location: str
    password: str
    email: str

class UserOut(BaseModel):
    id: int
    phone: str
    business_name: str
    location: str
    email: str
    is_verified: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str  # Changed to email
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True