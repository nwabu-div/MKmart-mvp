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
    orders = db.query(Order).filter(Order.seller_id == current_user.id).all()
    
    if not orders:
        return {"message": "No sales yet — start recording sales to get smart restock alerts!"}
    
    # Track sales per product (not just category)
    product_sales = defaultdict(float)       # product_id -> total revenue
    category_sales = defaultdict(float)      # category -> total revenue
    total_revenue = 0.0
    
    for order in orders:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                revenue = item.quantity * item.price_at_purchase
                product_sales[item.product_id] += revenue
                category_sales[product.category] += revenue
                total_revenue += revenue
    
    if total_revenue == 0:
        return {"message": "No revenue recorded yet — keep selling!"}
    
    # Find top category
    top_category = max(category_sales, key=category_sales.get)
    category_percentage = (category_sales[top_category] / total_revenue) * 100
    
    # Find top-selling products in the top category
    top_products = []
    for prod_id, revenue in sorted(product_sales.items(), key=lambda x: x[1], reverse=True):
        product = db.query(Product).filter(Product.id == prod_id).first()
        if product and product.category == top_category:
            top_products.append({
                "name": product.name,
                "revenue": round(revenue, 2),
                "stock_left": product.quantity_in_stock,
                "low_stock": product.quantity_in_stock <= 5  # You fit change threshold to 10 or whatever
            })
        if len(top_products) >= 3:  # Limit to top 3 products
            break
    
    # Build message
    message = f"{top_category} dey hot pass! 🔥 E carry {category_percentage:.1f}% of your total sales ({round(total_revenue, 2):,} NGN).\n\n"
    
    if top_products:
        message += "Top sellers for restock:\n"
        for p in top_products:
            message += f"- {p['name']}: {p['revenue']:,} NGN sold\n"
            if p['low_stock']:
                message += "   ⚠️ STOCK DEY LOW O! Buy more sharp sharp!\n"
            else:
                message += "   Stock still okay.\n"
    
    # Extra low stock alert if any hot product dey low
    low_stock_products = [p['name'] for p in top_products if p['low_stock']]
    if low_stock_products:
        message += "\nURGENT: " + ", ".join(low_stock_products) + " dey finish fast — restock NOW before customers vex! ⏰"
    
    return {
        "top_category": top_category,
        "category_percentage": round(category_percentage, 1),
        "total_revenue": round(total_revenue, 2),
        "top_products": top_products,  # For frontend later
        "message": message,
        "category_breakdown": dict(category_sales)
    }