from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import auth, products, inventory, orders


app = FastAPI(
    title="MokoMarket Electronics MVP - Backend Live!",
    description="Smart marketplace for electronics sellers with AI restock alerts",
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fresh DB on every deploy (fix old schema error on Render)
@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)

@app.get("/")
def home():
    return {
        "message": "MokoMarket Electronics MVP Backend dey live! 🚀 Go /docs make you test am",
        "docs": "/docs",
        "redoc": "/redoc"
    }