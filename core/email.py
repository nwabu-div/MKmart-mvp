from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from datetime import datetime
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_otp_email(email_to: EmailStr, otp: str):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #4CAF50;">MokoMarket</h1>
        </div>
        <div style="background: #f8f8f8; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #4CAF50;">Email Verification</h2>
            <p>Hello,</p>
            <p>Your one-time verification code is:</p>
            <h1 style="text-align: center; color: #4CAF50;">{otp}</h1>
            <p>This code expires in 5 minutes. If you didn't request this, please ignore this email.</p>
        </div>
        <div style="text-align: center; font-size: 12px; color: #666;">
            © {datetime.now().year} MokoMarket. All rights reserved.
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="MokoMarket Email Verification OTP",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    await fm.send_message(message)