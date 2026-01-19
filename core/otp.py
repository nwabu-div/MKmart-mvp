import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import OTP, User

def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP"""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def create_and_save_otp(db: Session, user: User) -> OTP:
    """Create OTP, save to DB, return the object"""
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 min expiry
    
    otp = OTP(
        user_id=user.id,
        code=code,
        expires_at=expires_at,
        attempts=0,
        last_resend_at=None
    )
    
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp

def verify_otp(db: Session, user_id: int, submitted_code: str) -> bool:
    """Check if OTP is valid, not expired, and delete it after success"""
    otp = db.query(OTP).filter(
        OTP.user_id == user_id,
        OTP.code == submitted_code,
        OTP.expires_at > datetime.utcnow()
    ).first()
    
    if otp:
        # Success: delete OTP (one-time use)
        db.delete(otp)
        db.commit()
        return True
    
    return False