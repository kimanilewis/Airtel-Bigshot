"""
Processing model for Airtel Kenya C2B IPN system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.database import Base


class ProcessingResult(Base):
    """
    Stores the processing results for each transaction.
    """
    __tablename__ = 'processing_results'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    is_processed = Column(Boolean, nullable=False)
    processing_message = Column(String(255), nullable=True)
    processing_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="processing_results")
