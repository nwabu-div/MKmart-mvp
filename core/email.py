from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# Debug: print environment variables to confirm loading
print("Loaded MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("Loaded MAIL_PASSWORD:", os.getenv("MAIL_PASSWORD"))
print("Loaded MAIL_SERVER:", os.getenv("MAIL_SERVER"))
print("Loaded MAIL_FROM:", os.getenv("MAIL_FROM"))

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() in ("true", "1", "yes"),
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() in ("true", "1", "yes"),
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True").lower() in ("true", "1", "yes"),
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "True").lower() in ("true", "1", "yes")
)

class EmailSchema(BaseModel):
    email: List[EmailStr]