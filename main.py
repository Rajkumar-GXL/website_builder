# Import Necessary Libraries.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from core.database import ROOT_ENGINE, master_engine
from website_creator.router import router as builder_router
from tenant.router import router as tenant_router
from master.models import MasterBase
import os
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="AI Website Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create master DB at startup
@app.on_event("startup")
def startup():
    with ROOT_ENGINE.connect().execution_options(autocommit=True) as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS master_db"))

    MasterBase.metadata.create_all(bind=master_engine)

# Static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# API Routers
app.include_router(builder_router, prefix="/api")
app.include_router(tenant_router, prefix="/api")

@app.get("/website-builder/")
def website_builder_ui(request: Request):
    return templates.TemplateResponse(
        "website_builder.html",
        {"request": request}
    )

@app.get("/")
def root():
    return {"message": "AI Website Builder Running"}

generated_sites_path = os.path.join(os.path.dirname(__file__), "generated_sites")

if os.path.exists(generated_sites_path):
    app.mount(
        "/sites",
        StaticFiles(directory=generated_sites_path),
        name="sites"
    )
