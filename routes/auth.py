from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.otp import generate_otp
from core.email import send_otp_email

router = APIRouter(prefix="/users", tags=["Authentication"])

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check duplicates
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone and db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Create user (not verified yet)
    hashed = hash_password(user.password)
    new_user = User(
        email=user.email,
        phone=user.phone,
        business_name=user.business_name,
        location=user.location,
        password_hash=hashed,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate and send OTP
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    new_user.otp_code = otp
    new_user.otp_expires_at = expires_at
    db.commit()

    # Send email (async)
    import asyncio
    asyncio.create_task(send_otp_email(user.email, otp))

    return {"message": "User created! Check your email for OTP to verify."}

@router.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    if user.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    return {"message": "Email verified successfully! You can now login."}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first with OTP")
    
    token = create_access_token(
        {"sub": str(db_user.id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}