from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: float
    merchant_id: str
    customer_id: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    is_fraudulent: bool
    fraud_score: Optional[float] = None

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    email: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: str

    class Config:
        from_attributes = True

class MerchantBase(BaseModel):
    name: str
    category: str

class MerchantCreate(MerchantBase):
    pass

class Merchant(MerchantBase):
    id: str

    class Config:
        from_attributes = True 