from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Product, Order, OrderItem, User
from core.dependencies import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/alerts/")
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seller_id = current_user.id

    sales_data = (
        db.query(Product.category, OrderItem.quantity)
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Product.seller_id == seller_id)
        .all()
    )

    if not sales_data:
        return {
            "message": "No sales yet — add some orders to see AI alerts! 📊"
        }

    category_sales = {}
    for category, qty in sales_data:
        category_sales[category] = category_sales.get(category, 0) + qty

    total_sales = sum(category_sales.values())
    top_category = max(category_sales, key=category_sales.get)
    top_percentage = round(
        (category_sales[top_category] / total_sales) * 100
    )

    alert = (
        f"{top_category} dey hot! "
        f"E carry {top_percentage}% of your sales. "
        f"Restock am sharp sharp! 🔥"
    )

    return {
        "top_selling_category": top_category,
        "percentage": top_percentage,
        "alert": alert,
        "full_breakdown": category_sales
    }
