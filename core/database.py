# Import necessary libraries
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from core.config import settings

# Maser database setup
master_engine = create_engine(settings.master_db_url, pool_pre_ping=True)
MasterSessionLocal = sessionmaker(bind=master_engine)

ROOT_ENGINE = create_engine(settings.mysql_root_url, pool_pre_ping=True)

TENANT_ENGINES = {}
TENANT_SESSIONS = {}

# Function to get master database session
def get_master_db():
    db = MasterSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to get tenant database session
def create_tenant_database(tenant_name: str):
    if not tenant_name.replace("_","").isalnum():
        raise ValueError("Invalid tenant name")
    with ROOT_ENGINE.connect().execution_options(autocommit=True) as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{tenant_name}`"))

# Function to get tenant database engine
def get_tenant_engine(tenant_db: str):
    if tenant_db not in TENANT_ENGINES:
        if settings.mysql_password:
            encoded_pwd = quote_plus(settings.mysql_password)
            url = f"mysql+pymysql://{settings.mysql_user}:{encoded_pwd}@{settings.mysql_host}:{settings.mysql_port}/{tenant_db}"
        else:
            url = f"mysql+pymysql://{settings.mysql_user}@{settings.mysql_host}:{settings.mysql_port}/{tenant_db}"

        TENANT_ENGINES[tenant_db] = create_engine(url, pool_pre_ping=True)

    return TENANT_ENGINES[tenant_db]

# Function to get tenant database session
def get_tenant_db(tenant_db: str):
    if tenant_db not in TENANT_SESSIONS:
        engine = get_tenant_engine(tenant_db)
        TENANT_SESSIONS[tenant_db] = sessionmaker(bind=engine)
    SessionLocal = TENANT_SESSIONS[tenant_db]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper functions to get categories and subcategories for website builder dropdowns
def get_categories():
    db = MasterSessionLocal()
    try:
        result = db.execute(text("SELECT id, name FROM categories ORDER BY name")).fetchall()
        return [{"id": r[0], "name": r[1]} for r in result]
    except Exception as e:
        print(f"DB Error: {e}")
        return []
    finally:
        db.close()


# Helper function to get subcategories based on selected category for website builder dropdowns
def get_subcategories(category_id: int):
    db = MasterSessionLocal()
    try:
        result = db.execute(text("SELECT id, name FROM sub_categories WHERE category_id = :cid ORDER BY name"), {"cid": category_id}).fetchall()
        return [{"id": r[0], "name": r[1]} for r in result]
    except:
        return []
    finally:
        db.close()


# Function to get master database connection
def get_master_connection():
    with master_engine.connect() as conn:
        yield conn







