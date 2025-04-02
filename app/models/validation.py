"""
Validation model for Airtel Kenya C2B IPN system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.database import Base


class ValidationResult(Base):
    """
    Stores the validation results for each transaction.
    """
    __tablename__ = 'validation_results'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    is_valid = Column(Boolean, nullable=False)
    validation_message = Column(String(255), nullable=True)
    validation_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="validation_results")
