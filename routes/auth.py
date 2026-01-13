from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import asyncio
from pydantic import BaseModel

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut, UserUpdate
from core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.otp import create_and_save_otp  # ← new import
from core.email import conf, FastMail, MessageSchema  # ← new import for email
from core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users & Auth"])

# Sign up
@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email or phone already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone and db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Hash password and create user
    hashed = hash_password(user.password)
    new_user = User(
        **user.dict(exclude={"password"}),
        password_hash=hashed,
        is_verified=False  # important!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate and save OTP
    otp = create_and_save_otp(db, new_user)

    # Send OTP email
    message = MessageSchema(
        subject="MokoMarket - Your Verification Code",
        recipients=[new_user.email],
        body=f"Your OTP code is: {otp.code}\n\nThis code expires in 10 minutes. Enter it to verify your email.",
        subtype="plain"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)  # send async

    # Return token (frontend will prompt for OTP next)
    token = create_access_token(
        {"sub": str(new_user.id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, "token_type": "bearer"}

class VerifyOTP(BaseModel):
    code: str

@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTP,                     # ← now expects JSON body
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.is_verified:
        return {"message": "Your email is already verified."}

    from core.otp import verify_otp

    if verify_otp(db, current_user.id, data.code):
        current_user.is_verified = True
        db.commit()
        db.refresh(current_user)
        return {"message": "Email verified successfully! You can now use full features."}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP. Please request a new one."
        )

# Login
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not db_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Check your inbox for OTP or signup again."
        )
    
    token = create_access_token({"sub": str(db_user.id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

# Get My Profile
@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Update My Profile
@router.patch("/me", response_model=UserOut)
def update_profile(
    update_data: UserUpdate,  # Change from UserCreate to UserUpdate
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_dict = update_data.dict(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    # Special checks for unique fields if they are being changed
    if "email" in update_dict and update_dict["email"] != current_user.email:
        if db.query(User).filter(User.email == update_dict["email"]).first():
            raise HTTPException(status_code=400, detail="Email already taken")

    if "phone" in update_dict and update_dict["phone"] != current_user.phone:
        if update_dict["phone"] and db.query(User).filter(User.phone == update_dict["phone"]).first():
            raise HTTPException(status_code=400, detail="Phone already taken")

    # Apply updates
    for key, value in update_dict.items():
        if key == "password" and value:
            setattr(current_user, "password_hash", hash_password(value))
        elif key != "password":
            setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user

# Delete My Account
@router.delete("/me")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}