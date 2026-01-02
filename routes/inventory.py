from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from database import get_db
from models import Product, Order, OrderItem, User
from core.dependencies import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/alerts/")
def get_restock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all orders for this seller
    orders = db.query(Order).filter(Order.seller_id == current_user.id).all()
    
    if not orders:
        return {"message": "No sales yet — start recording sales to get smart restock alerts!"}
    
    category_sales = defaultdict(float)
    total_revenue = 0.0
    
    for order in orders:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                revenue = item.quantity * item.price_at_purchase
                category_sales[product.category] += revenue
                total_revenue += revenue
    
    if total_revenue == 0:
        return {"message": "No revenue recorded yet — keep selling!"}
    
    top_category = max(category_sales, key=category_sales.get)
    percentage = (category_sales[top_category] / total_revenue) * 100
    
    message = (
        f"{top_category} dey hot pass! "
        f"E carry {percentage:.1f}% of your sales — "
        f"restock {top_category.lower()} sharp sharp before stock finish!! 🔥"
    )
    
    return {
        "top_category": top_category,
        "percentage": round(percentage, 1),
        "total_revenue": round(total_revenue, 2),
        "message": message,
        "breakdown": dict(category_sales)
    }