# Import necessary libraries
import os
import json
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from core.database import get_tenant_db, get_master_db

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Helper function to resolve tenant database based on website slug
async def resolve_tenant(website: str, master_db=Depends(get_master_db)):
    result = master_db.execute(
        text("SELECT db_name FROM websites WHERE slug = :slug"),
        {"slug": website}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Website not found")
    tenant_db = result[0]
    db_gen = get_tenant_db(tenant_db)
    db = next(db_gen)
    try:
        yield db
    finally:
        db.close()



# Function to get the homepage of the website which is present in the tenant db
@router.get("/{website}/", response_class=HTMLResponse)
async def tenant_home(request: Request, website: str, db=Depends(resolve_tenant)):
  
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "templates", "tenants", f"{website}.json")
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        # Default fallback if config missing
        config = {
            "theme": {"primary_color": "blue", "font_family": "Arial", "bg_color": "#f9f9f9"},
            "content": {"hero_headline": "Welcome", "hero_subheadline": "Great products"}
        }
        
        
    products = db.execute(text("""
        SELECT id, title, mrp, special_price, stock_count,
            stock_status, created_at, image_url, sub_category_id
        FROM products
        ORDER BY created_at DESC
        LIMIT 20
    """)).fetchall()
        
    products = [{
        "id": row[0],
        "title": row[1],
        "mrp": float(row[2] or 0),
        "special_price": float(row[3] or 0),
        "stock_count": row[4],
        "stock_status": row[5],
        "created_at": row[6],
        "image_url": row[7] or "",
        "sub_category_id": row[8]
    } for row in products]
        
        
    return templates.TemplateResponse("tenant_base.html", {
        "request": request,
        "website_title": website.replace("website_", "").replace("_", " ").title(),
        "website_slug": website,
        "config": config,    # AI Theme Data
        "products": products # DB Product Data
    })


# Fetch all products for a tenant.
@router.get("/{website}/products")
async def get_all_products(
    website: str = Path(...),
    db=Depends(resolve_tenant)
):
    try:
        result = db.execute(text("""
            SELECT 
                id,
                name,
                title,
                mrp,
                special_price,
                stock_count,
                stock_status,
                image_url,
                created_at
            FROM products
            ORDER BY created_at DESC
        """)).fetchall()

        products = []
        for row in result:
            products.append({
                "id": row[0],
                "name": row[1],
                "title": row[2],
                "mrp": float(row[3] or 0),
                "special_price": float(row[4] or 0),
                "stock_count": row[5],
                "stock_status": row[6],
                "image_url": row[7] or "",
                "created_at": str(row[8])
            })

        return {
            "success": True,
            "website": website,
            "total_products": len(products),
            "products": products
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }




# Function to get the product details which is present in the tenant db
@router.get("/{website}/product/{product_id}")
async def product_detail(
    website: str = Path(...),
    product_id: int = Path(...),
    db=Depends(resolve_tenant)
):
    try:
        result = db.execute(text("""
            SELECT 
                id,
                name,
                title,
                mrp,
                special_price,
                stock_count,
                stock_status,
                image_url,
                created_at
            FROM products
            WHERE id = :id
        """), {"id": product_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Product not found")

        return {
            "product": {
                "id": result[0],
                "name": result[1],
                "title": result[2],
                "mrp": float(result[3] or 0),
                "special_price": float(result[4] or 0),
                "stock_count": result[5],
                "stock_status": result[6],
                "image_url": result[7] or "",
                "created_at": str(result[8])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Function to add the product to the wishlist which is present in the tenant db
@router.post("/{website}/wishlist/{product_id}")
async def add_to_wishlist(website: str = Path(...), product_id: int = Path(...), db=Depends(resolve_tenant)):
    try:
        product_check = db.execute(text("SELECT id FROM products WHERE id = :pid"), {"pid": product_id}).fetchone()
        if not product_check:
            return {"error": "Product not found"}
        
        db.execute(text("""
            INSERT INTO wishlist (product_id, user_session) 
            VALUES (:pid, 'demo_session')
            ON DUPLICATE KEY UPDATE created_at = NOW()
        """), {"pid": product_id})
        db.commit()
        return {"success": True, "message": f"Added '{product_id}' to wishlist ✅"}
    except Exception as e:
        return {"error": str(e)}

# Function to get the wishlist items which is present in the tenant db
@router.get("/{website}/wishlist")
async def get_wishlist(website: str = Path(...), db=Depends(resolve_tenant)):
    try:
        result = db.execute(text("""
            SELECT w.id, w.product_id, w.created_at, p.title, p.special_price, p.image_url
            FROM wishlist w 
            JOIN products p ON w.product_id = p.id 
            WHERE w.user_session = 'demo_session'
            ORDER BY w.created_at DESC
        """)).fetchall()
        
        wishlist = []
        for row in result:
            wishlist.append({
                "wishlist_id": row[0],
                "product_id": row[1],
                "added_date": str(row[2]),
                "product": {
                    "title": row[3],
                    "price": float(row[4] or 0),
                    "image": row[5] or ""
                }
            })
        
        return {
            "wishlist": wishlist,
            "total_items": len(wishlist),
            "message": f"{len(wishlist)} items in wishlist"
        }
    except Exception as e:
        return {"wishlist": [], "total_items": 0, "error": str(e)}


# Function to remove the product from the wishlist which is present in the tenant db
@router.delete("/{website}/wishlist/{product_id}")
async def remove_from_wishlist(website: str = Path(...), product_id: int = Path(...), db=Depends(resolve_tenant)):
    try:
        deleted = db.execute(text("""
            DELETE FROM wishlist 
            WHERE product_id = :pid AND user_session = 'demo_session'
        """), {"pid": product_id}).rowcount
        
        db.commit()
        
        if deleted > 0:
            return {
                "success": True,
                "message": f"Removed '{product_id}' from wishlist",
                "product_id": product_id
            }
        else:
            return {
                "success": False,
                "message": f"Product '{product_id}' not in wishlist"
            }
    except Exception as e:
        return {"error": str(e)}


# Function to get the cart items which is present in the tenant db
@router.post("/{website}/cart/{product_id}")
async def add_to_cart(website: str = Path(...), product_id: int = Path(...), db=Depends(resolve_tenant)):
    try:
        product = db.execute(text("""
            SELECT stock_count, stock_status 
            FROM products 
            WHERE id = :pid
        """), {"pid": product_id}).fetchone()

        if not product:
            return {"error": "Product not found"}

        if product[1] == "Out of Stock":
            return {"error": "Product is out of stock"}
        
        # Add or update cart item
        current = db.execute(text("""
            SELECT quantity FROM cart
            WHERE product_id = :pid AND user_session = 'demo_session'
        """), {"pid": product_id}).fetchone()

        current_qty = current[0] if current else 0

        if current_qty + 1 > product[0]:  # product[0] = stock_count
            return {"error": "Cannot add more than available stock"}

        if current:
            db.execute(text("""
                UPDATE cart
                SET quantity = quantity + 1
                WHERE product_id = :pid AND user_session = 'demo_session'
            """), {"pid": product_id})
        else:
            db.execute(text("""
                INSERT INTO cart (product_id, user_session, quantity)
                VALUES (:pid, 'demo_session', 1)
            """), {"pid": product_id})
        db.commit()
        return {"success": True, "message": f"Added '{product_id}' to cart 🛒"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/{website}/cart")
async def get_cart(website: str = Path(...), db=Depends(resolve_tenant)):
    try:
        result = db.execute(text("""
            SELECT c.id, c.product_id, c.quantity, c.created_at, 
                   p.title, p.special_price, p.image_url
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_session = 'demo_session'
            ORDER BY c.created_at DESC
        """)).fetchall()
        
        cart_items = []
        for row in result:
            cart_items.append({
                "cart_id": row[0],
                "product_id": row[1],
                "quantity": row[2],
                "added_date": str(row[3]),
                "product": {
                    "title": row[4],
                    "price": float(row[5] or 0),
                    "image": row[6] or ""
                }
            })
        
        total = sum(item["quantity"] * item["product"]["price"] for item in cart_items)
        return {
            "cart": cart_items,
            "total_items": len(cart_items),
            "total_price": round(total, 2),
            "message": f"{len(cart_items)} items in cart"
        }
    except Exception as e:
        return {"cart": [], "total_items": 0, "error": str(e)}


# Function to remove the product from the cart which is present in the tenant db
@router.delete("/{website}/cart/{product_id}")
async def remove_from_cart(website: str = Path(...), product_id: int = Path(...), db=Depends(resolve_tenant)):
    try:
        deleted = db.execute(text("""
            DELETE FROM cart 
            WHERE product_id = :pid AND user_session = 'demo_session'
        """), {"pid": product_id}).rowcount
        
        db.commit()
        
        if deleted > 0:
            return {
                "success": True,
                "message": f"Removed '{product_id}' from cart",
                "product_id": product_id
            }
        else:
            return {
                "success": False,
                "message": f"Product '{product_id}' not in cart"
            }
    except Exception as e:
        return {"error": str(e)}
    

# Function to get the checkout page which is present in the tenant db
@router.post("/{website}/checkout")
async def process_checkout(website: str = Path(...), db=Depends(resolve_tenant)):
    try:
        result = db.execute(text("""
            SELECT c.product_id, c.quantity, p.title, p.special_price, p.stock_count
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_session = 'demo_session'
        """)).fetchall()

        if not result:
            return {"error": "Cart is empty - nothing to checkout"}

        order_items = []
        subtotal = 0

        # 🔒 STOCK VALIDATION + DEDUCTION
        for row in result:
            product_id = row[0]
            quantity = row[1]
            title = row[2]
            price = float(row[3] or 0)
            stock_available = row[4]

            update_result = db.execute(text("""
                UPDATE products
                SET 
                    stock_count = stock_count - :qty,
                    stock_status = CASE 
                        WHEN stock_count - :qty <= 0 THEN 'Out of Stock'
                        ELSE stock_status
                    END
                WHERE id = :pid AND stock_count >= :qty
            """), {"qty": quantity, "pid": product_id})

            if update_result.rowcount == 0:
                db.rollback()
                return {
                    "error": f"Stock changed. Not enough stock for {title}"
                }

            item_total = quantity * price
            subtotal += item_total

            order_items.append({
                "product_id": product_id,
                "title": title,
                "quantity": quantity,
                "price": price,
                "total": item_total
            })

        tax = subtotal * 0.18
        grand_total = subtotal + tax

        import time
        order_id = f"ORD_{int(time.time())}"

        # Clear cart AFTER stock deduction
        db.execute(text("DELETE FROM cart WHERE user_session = 'demo_session'"))

        db.commit()

        return {
            "success": True,
            "message": "Order placed successfully! 🎉",
            "order": {
                "order_id": order_id,
                "items": order_items,
                "subtotal": round(subtotal, 2),
                "tax_gst": round(tax, 2),
                "grand_total": round(grand_total, 2),
                "status": "confirmed",
                "timestamp": str(time.time())
            }
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


@router.post("/{website}/register")
async def register_user(
    website: str,
    payload: RegisterRequest,
    db=Depends(resolve_tenant)
):
    existing = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": payload.email}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(payload.password)

    db.execute(
        text("""
            INSERT INTO users (name, email, password_hash)
            VALUES (:name, :email, :pwd)
        """),
        {
            "name": payload.name,
            "email": payload.email,
            "pwd": hashed_pwd
        }
    )

    db.commit()

    return {"success": True, "message": "User registered successfully"}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/{website}/login")
async def login_user(
    website: str,
    payload: LoginRequest,
    db=Depends(resolve_tenant)
):
    user = db.execute(
        text("SELECT id, password_hash FROM users WHERE email = :email"),
        {"email": payload.email}
    ).fetchone()

    if not user or not verify_password(payload.password, user[1]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "success": True,
        "user_id": user[0],
        "message": "Login successful"
    }
