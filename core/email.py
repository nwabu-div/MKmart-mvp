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
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .otp {{ font-size: 32px; font-weight: bold; color: #4CAF50; text-align: center; margin: 30px 0; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>MokoMarket</h1>
            </div>
            <h2>Hello,</h2>
            <p>Your verification code is:</p>
            <div class="otp">{otp}</div>
            <p>This code expires in 10 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <div class="footer">
                © {datetime.now().year} MokoMarket. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="MokoMarket Email Verification",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    await fm.send_message(message)