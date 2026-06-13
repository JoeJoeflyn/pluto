import datetime
import os

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("PLUTO_DB_URL", "sqlite:///./expenses.db")

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


class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    first_seen = Column(Date, default=datetime.date.today)
    last_seen = Column(Date, default=datetime.date.today)
    visit_count = Column(Integer, default=1)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    time = Column(String, nullable=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    tip = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    payment_method = Column(String, nullable=True)
    card_type = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)
    cashier = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    reference_id = Column(String, nullable=True)
    auth_id = Column(String, nullable=True)
    category = Column(String)
    merchant = Column(String)
    notes = Column(String)
    image_path = Column(String)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    raw_text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    synced_at = Column(DateTime, nullable=True)

    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True)
    merchant_rel = relationship("Merchant")

    items = relationship(
        "LineItem", back_populates="expense", cascade="all, delete-orphan",
        order_by="LineItem.order_index",
    )


class LineItem(Base):
    __tablename__ = "line_items"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    order_index = Column(Integer, default=0)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    category = Column(String, nullable=True)

    expense = relationship("Expense", back_populates="items")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    default_categories = [
        ("Food & Dining", "🍔"), ("Shopping", "🛒"), ("Transportation", "🚗"),
        ("Housing", "🏠"), ("Health", "💊"), ("Entertainment", "🎬"),
        ("Utilities", "📱"), ("Other", "💰"),
    ]
    for name, icon in default_categories:
        existing = db.query(Category).filter(Category.name == name).first()
        if not existing:
            db.add(Category(name=name, icon=icon))
    db.commit()
    db.close()
