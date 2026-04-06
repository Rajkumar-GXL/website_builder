# Import necessary modules and dependencies
import os
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy import text
from core.database import create_tenant_database, get_master_db
from core.database import get_categories as fetch_categories  
from core.database import get_subcategories as fetch_subcategories 
from core.tenant_manager import seed_tenant_data
from services.ai_generator import ai_generator
from services.website_repair import WebsiteRepairAgent

router = APIRouter(prefix="/website-builder", tags=["Website Builder"])

BASE_DIR = Path(__file__).resolve().parent.parent
SITES_DIR = BASE_DIR / "sites"

# Initialize repair agent once
repair_agent = WebsiteRepairAgent(ai_generator, SITES_DIR)

# Pydantic model for the create website request
class CreateWebsiteRequest(BaseModel):
    website_title: str
    category_id: int
    subcategory_id: int
    

# Helper to generate slug
def generate_slug(title: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '', title.replace(" ", "_"))
    return f"website_{cleaned.lower()}"

# Endpoints to fetch categories and subcategories for dropdowns in the website builder form
@router.get("/categories")
def get_categories():
    return {"categories": fetch_categories()}


# Endpoint to fetch subcategories based on selected category for dropdowns in the website builder form
@router.get("/subcategories/{category_id}")
def get_subcategories(category_id: int):
    return {"subcategories": fetch_subcategories(category_id)}


# Endpoint to create a new website based on user input and AI generation
# Endpoint to create a new website with auto‑repair
@router.post("/create-website")
async def create_website(request: CreateWebsiteRequest, master_db=Depends(get_master_db)):
    slug = generate_slug(request.website_title)
    tenant_db = slug

    # Check if already exists
    existing = master_db.execute(
        text("SELECT id FROM websites WHERE slug = :slug"),
        {"slug": slug}
    ).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Website already exists")

    # Get category/subcategory names
    cat = master_db.execute(
        text("SELECT name FROM categories WHERE id = :id"),
        {"id": request.category_id}
    ).fetchone()
    category_name = cat[0] if cat else "General"

    # 1. Create tenant database and seed products
    create_tenant_database(tenant_db)
    seed_tenant_data(tenant_db, request.subcategory_id)

    # 2. Generate initial website via AI
    app_data = ai_generator.generate_full_application(
        slug,
        request.website_title,
        category_name
    )
    if not app_data or not app_data.get("success"):
        raise HTTPException(status_code=500, detail=f"AI generation failed: {app_data}")

    # 3. Save generated files
    site_dir = SITES_DIR / slug
    site_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in app_data["files"].items():
        file_path = site_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content or "")

    # 4. Insert website record into master DB (BEFORE repair so API routes work)
    master_db.execute(
        text("INSERT INTO websites (name, slug, db_name) VALUES (:name, :slug, :db)"),
        {"name": request.website_title, "slug": slug, "db": tenant_db}
    )
    master_db.commit()

    # 5. Run repair agent (now API calls will succeed)
    base_url = f"http://localhost:8000/sites/{slug}/index.html"
    repair_result = await repair_agent.repair(
        slug=slug,
        title=request.website_title,
        category=category_name,
        base_url=base_url
    )

    return {
        "success": True,
        "message": "Website generated and repaired successfully",
        "website_url": f"/sites/{slug}/index.html",
        "repair": {
            "attempted": repair_result.get("repair_attempted", False),
            "remaining_issues": repair_result.get("remaining_issues", [])
        }
    }

@router.get("/")
def builder_home():
    return {
        "service": "Website Builder API",
        "status": "running"
    }