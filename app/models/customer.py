"""
Customer model for Airtel Kenya C2B IPN system.
"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
import enum
import datetime

from app.database import Base


class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Customer(Base):
    """
    Stores customer KYC information including billRef and refType.
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    bill_ref = Column(String(100), nullable=False, index=True)
    ref_type = Column(String(50), nullable=False)
    msisdn = Column(String(20), nullable=False, index=True)  # Customer phone number
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    id_number = Column(String(50), nullable=True)  # National ID or passport
    address = Column(String(255), nullable=True)
    status = Column(Enum(CustomerStatus), nullable=False, default=CustomerStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, 
                        onupdate=datetime.datetime.utcnow)
    
    # Create a unique constraint on bill_ref and ref_type
    __table_args__ = (UniqueConstraint('bill_ref', 'ref_type', name='uix_bill_ref_ref_type'),)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
