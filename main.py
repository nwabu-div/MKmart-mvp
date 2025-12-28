from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List
from collections import defaultdict
import hashlib

from database import Base, engine, get_db
from models import User, Product, Order, OrderItem
from schemas import UserCreate, UserLogin, Token, ProductCreate, ProductOut, OrderCreate, OrderOut, OrderItemOut

app = FastAPI(title="MokoMarket Electronics MVP - Backend Live!")

# Create tables
@app.on_event("startup")
def on_startup():
    # Create tables if no exist
    Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")  # Change from bcrypt to pbkdf2_sha256

# JWT settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")  # For future token

SECRET_KEY = "your_super_secret_key_here_change_it"  # Change this to strong random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.phone == phone).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# === USER ENDPOINTS ===
@app.post("/users/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if phone already registered
    if db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Hash password (no truncate — bcrypt 4.1.3 work fine with short passwords)
    hashed_password = pwd_context.hash(user.password)
    print("NEW USER HASHED PASSWORD:", hashed_password)

    
    # Create user
    new_user = User(
        phone=user.phone,
        business_name=user.business_name,
        location=user.location,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully!", "user_id": new_user.id}

@app.post("/users/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone == user.phone).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect phone or password")

    print("=== LOGIN ATTEMPT DEBUG ===")
    print("Phone from request:", user.phone)
    print("Plain password from request:", user.password)
    print("Hashed password from DB:", db_user.password_hash)

    verified = verify_password(user.password, db_user.password_hash)
    print("Verification result:", verified)
    print("=============================")

    if not verified:
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.phone}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# === PRODUCT ENDPOINTS ===
@app.post("/products/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = Product(**product.dict(), seller_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only show products belonging to the logged-in seller
    return db.query(Product).filter(Product.seller_id == current_user.id).all()

# === AI INVENTORY ALERTS ===
@app.get("/inventory/alerts/")
def get_restock_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.buyer_id == current_user.id).all()  # or seller_id
    
    if not orders:
        return {"message": "No sales yet — start recording orders to get AI restock alerts!"}
    
    category_sales = defaultdict(float)
    total_revenue = 0
    
    for order in orders:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                category_sales[product.category] += item.quantity * item.price_at_purchase
                total_revenue += item.quantity * item.price_at_purchase
    
    if total_revenue == 0:
        return {"message": "No revenue yet — keep selling!"}
    
    top_category = max(category_sales, key=category_sales.get)
    percentage = (category_sales[top_category] / total_revenue) * 100
    
    message = f"{top_category} dey hot pass! E carry {percentage:.1f}% of your sales — restock {top_category.lower()} sharp sharp before stock finish!! 🔥"
    
    return {
        "top_category": top_category,
        "percentage": round(percentage, 1),
        "message": message,
        "total_revenue": round(total_revenue, 2)
    }

@app.post("/orders/", response_model=OrderOut)
def record_sale(order_data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = 0
    order_items = []

    for item in order_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.seller_id == current_user.id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found or not yours")
        
        if product.quantity_in_stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
        
        # Reduce stock
        product.quantity_in_stock -= item.quantity
        
        # Calculate item total
        item_total = item.quantity * item.price_at_purchase
        total += item_total
        
        # Create order item
        db_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase
        )
        order_items.append(db_item)
    
    # Create order
    new_order = Order(
        buyer_id=current_user.id,  # or seller_id if you wan track seller
        total_amount=total,
        status="completed"
    )
    db.add(new_order)
    db.flush()  # get order id
    
    # Link items to order
    for item in order_items:
        item.order_id = new_order.id
        db.add(item)
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@app.get("/")
def home():
    return {"message": "MokoMarket Electronics MVP Backend Dey Live! Go /docs make you test am 🚀"}