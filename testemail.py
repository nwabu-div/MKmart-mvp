import asyncio
from core.email import conf, FastMail, MessageSchema

async def test_send():
    message = MessageSchema(
        subject="Test from MokoMarket",
        recipients=["ngbodinjoshua@gmail.com"],  # ← quotes around the email!
        body="This na test email from your MVP backend. If you see am, SMTP dey work! 🚀",
        subtype="plain"
    )
    
    print("Sending to:", message.recipients)  # extra debug
    
    fm = FastMail(conf)
    await fm.send_message(message)
    print("Email sent successfully!")

if __name__ == "__main__":
    asyncio.run(test_send())