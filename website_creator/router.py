# Import necessary modules and dependencies
import os
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from core.database import create_tenant_database, get_master_db
from core.database import get_categories as fetch_categories  
from core.database import get_subcategories as fetch_subcategories 
from core.tenant_manager import seed_tenant_data
from services.ai_generator import ai_generator

router = APIRouter(prefix="/website-builder", tags=["Website Builder"])

# Pydantic model for the create website request
class CreateWebsiteRequest(BaseModel):
    website_title: str
    category_id: int
    subcategory_id: int
    

# Endpoints to fetch categories and subcategories for dropdowns in the website builder form
@router.get("/categories")
def get_categories():
    return {"categories": fetch_categories()}


# Endpoint to fetch subcategories based on selected category for dropdowns in the website builder form
@router.get("/subcategories/{category_id}")
def get_subcategories(category_id: int):
    return {"subcategories": fetch_subcategories(category_id)}


# Endpoint to create a new website based on user input and AI generation
@router.post("/create-website")
def create_website(request: CreateWebsiteRequest, master_db=Depends(get_master_db)):
    def generate_slug(title: str):
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', title.replace(" ", "_"))
        return f"website_{cleaned.lower()}"

    slug = generate_slug(request.website_title)
    tenant_db = slug

    # Check existing
    existing = master_db.execute(
        text("SELECT id FROM websites WHERE slug=:slug"),
        {"slug": slug}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Website already exists")

    # Get category/subcategory names
    cat = master_db.execute(
        text("SELECT name FROM categories WHERE id=:id"),
        {"id": request.category_id}
    ).fetchone()

    subcat = master_db.execute(
        text("SELECT name FROM sub_categories WHERE id=:id"),
        {"id": request.subcategory_id}
    ).fetchone()

    category_name = cat[0] if cat else "General"
    subcategory_name = subcat[0] if subcat else "Products"

    # Create tenant DB
    create_tenant_database(tenant_db)

    # Seed data
    seed_tenant_data(tenant_db, request.subcategory_id)

    # Generate AI config
    app_data = ai_generator.generate_full_application(
        slug,
        request.website_title,
        category_name
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sites_dir = os.path.join(base_dir, "sites", slug)

    os.makedirs(sites_dir, exist_ok=True)

    if not app_data or "files" not in app_data:
        raise HTTPException(
            status_code=500,
            detail=f"AI failed: {app_data}"
        )

    for filename, filecontent in app_data["files"].items():
        file_path = os.path.join(sites_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(filecontent or "")


    # Insert into master DB
    master_db.execute(
        text("INSERT INTO websites (name, slug, db_name) VALUES (:name,:slug,:db)"),
        {"name": request.website_title, "slug": slug, "db": tenant_db}
    )
    master_db.commit()

    return {
        "success": True,
        "message": "Website generated successfully!",
        "website_url": f"/sites/{slug}/index.html"
    }

@router.get("/")
def builder_home():
    return {
        "service": "Website Builder API",
        "status": "running"
    }