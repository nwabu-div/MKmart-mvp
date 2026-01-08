from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut
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
@router.put("/me", response_model=UserOut)
def update_profile(
    update_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if update_data.email != current_user.email and db.query(User).filter(User.email == update_data.email).first():
        raise HTTPException(status_code=400, detail="Email already taken")
    if update_data.phone != current_user.phone and update_data.phone and db.query(User).filter(User.phone == update_data.phone).first():
        raise HTTPException(status_code=400, detail="Phone already taken")

    for key, value in update_data.dict(exclude_unset=True).items():
        if key != "password":
            setattr(current_user, key, value)
        else:
            setattr(current_user, "password_hash", hash_password(value))

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