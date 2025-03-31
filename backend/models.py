from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    timestamp = Column(DateTime)
    merchant_id = Column(String)
    customer_id = Column(String)
    is_fraudulent = Column(Boolean, default=False)
    fraud_score = Column(Float, nullable=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    transactions = relationship("Transaction", back_populates="customer")

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    transactions = relationship("Transaction", back_populates="merchant") 