from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
from datetime import datetime
import os




conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=f"Moko Market <{os.getenv('MAIL_USERNAME')}>",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fast_mail = FastMail(conf)


async def send_email(
    subject: str,
    recipients: List[EmailStr],
    body: str,
    html: bool = True,
):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html" if html else "plain",
    )

    await fast_mail.send_message(message)




def email_template(
    title: str,
    greeting_name: str,
    message: str,
    highlight: str,
    footer_note: str = "If you did not request this, please ignore this email.",
):
    year = datetime.now().year

    return f"""
    <div style="font-family: Arial, Helvetica, sans-serif; background-color: #f4f6f8; padding: 30px;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        
        <!-- Header -->
        <div style="background-color: #16a34a; padding: 20px; text-align: center;">
          <h1 style="color: #ffffff; margin: 0; font-size: 22px;">
            {title}
          </h1>
        </div>

        <!-- Body -->
        <div style="padding: 30px; color: #333333;">
          <p style="font-size: 16px; margin-top: 0;">
            Hello <strong>{greeting_name}</strong>,
          </p>

          <p style="font-size: 15px; line-height: 1.6;">
            {message}
          </p>

          <!-- Highlight Box (OTP / Code / Important Info) -->
          <div style="margin: 30px 0; text-align: center;">
            <span style="
              display: inline-block;
              font-size: 28px;
              letter-spacing: 6px;
              padding: 15px 25px;
              background-color: #f0fdf4;
              color: #16a34a;
              border: 1px dashed #16a34a;
              border-radius: 6px;
              font-weight: bold;
            ">
              {highlight}
            </span>
          </div>

          <p style="font-size: 14px; color: #555555; line-height: 1.6;">
            {footer_note}
          </p>

          <p style="font-size: 14px; margin-top: 30px;">
            Best regards,<br/>
            <strong>The MokoMarket Team</strong>
          </p>
        </div>

        <!-- Footer -->
        <div style="background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #777777;">
          © {year} MokoMarket. All rights reserved.
        </div>

      </div>
    </div>
    """
