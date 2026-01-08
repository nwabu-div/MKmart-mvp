# To Start the Server Locally
py -m uvicorn main:app --reload
# OR
uvicorn main:app --reload

# To Test Live
Use Postman or visit the live URL and go to /docs

# Environment Vars (Optional for now)
You fit add .env file with:
SECRET_KEY=your_very_long_random_secret_key_here

# Note
Signup and login dey instant — no email verification for this MVP!