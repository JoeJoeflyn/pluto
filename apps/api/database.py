import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    icon = Column(String)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    currency = Column(String, default="USD")
    category = Column(String)
    merchant = Column(String)
    notes = Column(String)
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Pre-seed categories
    default_categories = [
        ("Food & Dining", "🍔"), ("Shopping", "🛒"), ("Transportation", "🚗"),
        ("Housing", "🏠"), ("Health", "💊"), ("Entertainment", "🎬"),
        ("Utilities", "📱"), ("Other", "💰")
    ]
    for name, icon in default_categories:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            db.add(Category(name=name, icon=icon))
    db.commit()
    db.close()
