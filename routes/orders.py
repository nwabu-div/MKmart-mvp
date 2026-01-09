from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Order, OrderItem, Product, User
from schemas import OrderCreate, OrderOut
from core.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def record_sale(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    total_amount = 0.0
    order_items_to_create = []

    # Validate products and calculate total + prepare items
    for item in order_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.seller_id == current_user.id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")

        if product.quantity_in_stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}. Available: {product.quantity_in_stock}"
            )

        # Reduce stock
        product.quantity_in_stock -= item.quantity

        # Calculate amount for this item
        item_total = item.quantity * item.price_at_purchase
        total_amount += item_total

        # Prepare OrderItem
        order_items_to_create.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase
            )
        )

    # Create the Order
    new_order = Order(
        seller_id=current_user.id,
        total_amount=total_amount,
        status="completed"
    )
    db.add(new_order)
    db.flush()  # Get the order.id without committing yet

    # Link items to order
    for order_item in order_items_to_create:
        order_item.order_id = new_order.id

    db.add_all(order_items_to_create)
    db.commit()
    db.refresh(new_order)

    return new_order

@router.get("/", response_model=List[OrderOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all your recorded sales/orders, newest first
    """
    orders = (
        db.query(Order)
        .filter(Order.seller_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    
    if not orders:
        return []  # or raise 404 if you prefer, but empty list is fine for MVP
    
    return orders