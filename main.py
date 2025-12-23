from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List

from database import Base, engine, get_db
from models import User, Product, Order, OrderItem
from schemas import UserCreate, UserLogin, Token, ProductCreate, ProductOut

app = FastAPI(title="MokoMarket Electronics MVP - Backend Live!")

# Create tables
@app.on_event("startup")
def on_startup():
    # Create tables if no exist
    Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # For password hash

# JWT settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")  # For future token

SECRET_KEY = "your_super_secret_key_here_change_it"  # Change this to strong random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
            raise HTTPException(status_code=401, message="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, message="Invalid token")
    
    user = db.query(User).filter(User.phone == phone).first()
    if user is None:
        raise HTTPException(status_code=401, message="User not found")
    return user

# === USER ENDPOINTS ===
@app.post("/users/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, message="Phone number already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        phone=user.phone,
        business_name=user.business_name,
        location=user.location,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully!"}

@app.post("/users/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone == user.phone).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, message="Incorrect phone or password")
    
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
def get_inventory_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seller_id = current_user.id
    
    sales_data = db.query(
        Product.category,
        OrderItem.quantity
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Product.seller_id == seller_id).all()
    
    if not sales_data:
        return {"message": "No sales yet — add some orders to see AI alerts! 📊"}
    
    category_sales = {}
    for category, qty in sales_data:
        category_sales[category] = category_sales.get(category, 0) + qty
    
    total_sales = sum(category_sales.values())
    top_category = max(category_sales, key=category_sales.get)
    top_percentage = round((category_sales[top_category] / total_sales) * 100)
    
    alert = f"{top_category} dey hot! E carry {top_percentage}% of your sales. Restock am sharp sharp! 🔥"
    
    return {
        "top_selling_category": top_category,
        "percentage": top_percentage,
        "alert": alert,
        "full_breakdown": category_sales
    }

@app.get("/")
def home():
    return {"message": "MokoMarket Electronics MVP Backend Dey Live! Go /docs make you test am 🚀"}