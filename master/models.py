# Import Necessary Libraries.
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class MasterBase(DeclarativeBase):
    pass

# Class to represent the website which is present in the master db
class Website(MasterBase):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    db_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)