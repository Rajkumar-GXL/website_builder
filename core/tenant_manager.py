# Import Necessary Libraries
from sqlalchemy import text
from core.database import get_master_db
from tenant.models import Base
from core.database import get_tenant_engine
from passlib.context import CryptContext


# Function to seed tenant database with products based on selected subcategory
def seed_tenant_data(tenant_db: str, subcategory_id: int):

    master_db = next(get_master_db())
    try:
        products = master_db.execute(text("""
            SELECT id, name, title, mrp, special_price, stock_count, stock_status, image_url
            FROM products 
            WHERE sub_category_id = :subcat_id 
            LIMIT 50
        """), {"subcat_id": subcategory_id}).fetchall()
    finally:
        master_db.close()

    engine = get_tenant_engine(tenant_db)

    # Create tables from models
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        for product in products:
            conn.execute(text("""
                INSERT INTO products (
                    id,
                    sub_category_id,
                    name,
                    title,
                    mrp,
                    special_price,
                    stock_count,
                    stock_status,
                    created_at,
                    image_url
                )
                VALUES (
                    :id,
                    :subcat_id,
                    :name,
                    :title,
                    :mrp,
                    :special,
                    :stock,
                    :stock_status,
                    NOW(),
                    :image
                )
                ON DUPLICATE KEY UPDATE 
                    name = VALUES(name),
                    title = VALUES(title),
                    mrp = VALUES(mrp),
                    special_price = VALUES(special_price),
                    stock_count = VALUES(stock_count),
                    stock_status = VALUES(stock_status),
                    image_url = VALUES(image_url)
            """), {
                "id": product[0],
                "subcat_id": subcategory_id,
                "name": product[1],
                "title": product[2],
                "mrp": float(product[3] or 0),
                "special": float(product[4] or 0),
                "stock": int(product[5] or 0),
                "stock_status": "Out of Stock" if int(product[5] or 0) <= 0 else "In Stock",
                "image": product[7] or ""
            })
        conn.commit()

    print(f"SEED COMPLETE: {tenant_db} - {len(products)} products")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_users_table(tenant_db: str, default_admin: dict = None):
    """
    Create 'users' table for a tenant and optionally add a default admin user.
    """
    engine = get_tenant_engine(tenant_db)
    with engine.connect() as conn:
        # SQLAlchemy will create the table via Base.metadata.create_all()
        # Optional: keep manual create for safety
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        if default_admin:
            try:
                hashed_pwd = pwd_context.hash(default_admin["password"])
                conn.execute(text("""
                    INSERT INTO users (name, email, password_hash)
                    VALUES (:name, :email, :pwd)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), password_hash = VALUES(password_hash)
                """), {
                    "name": default_admin["name"],
                    "email": default_admin["email"],
                    "pwd": hashed_pwd
                })
                print(f"Default admin '{default_admin['email']}' created successfully")
            except Exception as e:
                print(f"Admin creation skipped: {e}")


def create_tenant_website(tenant_db: str, default_admin: dict = None):
    """
    Creates the tenant database tables including products and users.
    """
    engine = get_tenant_engine(tenant_db)

    # Create all tables from models
    Base.metadata.create_all(bind=engine)

    # Create users table and optional default admin
    create_users_table(tenant_db, default_admin=default_admin)

    print(f"Tenant '{tenant_db}' setup complete!")