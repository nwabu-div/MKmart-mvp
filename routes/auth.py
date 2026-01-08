from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut, UserUpdate
from core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users & Auth"])

# Sign up
@router.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone and db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    hashed = hash_password(user.password)

    user_data = user.dict(exclude={"password"})

    new_user = User(
        **user_data,
        password_hash=hashed,
        is_verified=True  # auto-verify for now
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        {"sub": str(new_user.id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": token, "token_type": "bearer"}

# Login
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
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