from fastapi import FastAPI

from database import Base, engine
from routes import auth, products, inventory

# App entry point
app = FastAPI(
    title="MokoMarket Electronics MVP - Backend Live!",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Register API routes
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)

# Health check / home
@app.get("/")
def home():
    return {
        "message": "MokoMarket Electronics MVP Backend dey live! 🚀 Go /docs make you test am"
    }
