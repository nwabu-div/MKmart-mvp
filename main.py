from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import auth, products, inventory

app = FastAPI(
    title="MokoMarket Electronics MVP - Backend Live!",
    description="Smart marketplace for electronics sellers with AI restock alerts",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create/drop tables on startup (fix schema on Render)
@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)  # Fresh start
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