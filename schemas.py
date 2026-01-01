from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# For creating new user
class UserCreate(BaseModel):
    phone: Optional[str] = None
    business_name: str
    location: str
    password: str
    email: str

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
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float  # price at time of sale

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

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
    items: list[OrderItemOut]

    class Config:
        from_attributes = True
        
