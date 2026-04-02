# Import necessary libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.database import ROOT_ENGINE, master_engine
from website_creator.router import router as builder_router
from tenant.router import router as tenant_router
from master.models import MasterBase
from sqlalchemy import text
import os

app = FastAPI(title="AI Website Builder")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Mount static files if the directory exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="app/templates")

# Startup
@app.on_event("startup")
def startup():
    with ROOT_ENGINE.connect().execution_options(autocommit=True) as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS master_db"))
    MasterBase.metadata.create_all(bind=master_engine)

# Include routers
app.include_router(builder_router)
app.include_router(tenant_router)

# End Point to start.
@app.get("/")
def builder_ui():
    return {"message":"Welcome to AI Website Builder"}
