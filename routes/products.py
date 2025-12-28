from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductOut
from core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = Product(
        **product.dict(),
        seller_id=current_user.id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("/", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only return products belonging to logged-in seller
    return (
        db.query(Product)
        .filter(Product.seller_id == current_user.id)
        .all()
    )
