from fastapi import FastAPI
from database import Base, engine
from routes import auth, products, inventory

app = FastAPI(
    title="MokoMarket Electronics MVP - Backend Live!",
    description="Smart marketplace for electronics sellers with AI restock alerts",
    version="1.0.0"
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)

@app.get("/")
def home():
    return {
        "message": "MokoMarket Electronics MVP Backend dey live! 🚀 Go /docs make you test am",
        "docs": "/docs",
        "redoc": "/redoc"
    }