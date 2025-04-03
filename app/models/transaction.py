"""
Fixed Transaction model with proper relationship to Customer.
"""
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
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
    Stores transaction data from Airtel Kenya C2B IPNs.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    bill_ref = Column(String(100), nullable=False, index=True)
    ref_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    msisdn = Column(String(20), nullable=False)  # Customer phone number
    merchant_msisdn = Column(String(20), nullable=True)  # Merchant phone number
    payment_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    currency = Column(String(10), nullable=False, default="KES")
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    airtel_reference = Column(String(100), nullable=True)  # Reference from Airtel
    mobiquity_reference = Column(String(100), nullable=True)  # Reference from Mobiquity
    raw_payload = Column(String, nullable=False)  # Raw request payload
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    
    # Define relationship with Customer
    customer = relationship("Customer", back_populates="transactions")
    
    # Define relationships with ValidationResult and ProcessingResult
    validation_results = relationship("ValidationResult", back_populates="transaction", cascade="all, delete-orphan")
    processing_results = relationship("ProcessingResult", back_populates="transaction", cascade="all, delete-orphan")
