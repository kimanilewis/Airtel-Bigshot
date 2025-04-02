"""
Transaction model for Airtel Kenya C2B IPN system.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.orm import relationship
import enum
import datetime

from app.database import Base


class TransactionStatus(enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    PROCESSED = "processed"
    FAILED = "failed"


class Transaction(Base):
    """
    Stores the transaction data received from Airtel Kenya C2B IPN.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    bill_ref = Column(String(100), nullable=False, index=True)
    ref_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    msisdn = Column(String(20), nullable=False)  # Customer phone number
    payment_date = Column(DateTime, nullable=False)
    currency = Column(String(10), nullable=False, default="KES")
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    raw_payload = Column(Text, nullable=False)  # Store the original JSON payload
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, 
                        onupdate=datetime.datetime.utcnow)
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="transaction", cascade="all, delete-orphan")
    processing_results = relationship("ProcessingResult", back_populates="transaction", cascade="all, delete-orphan")
