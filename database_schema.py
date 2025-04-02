"""
Database Schema for Airtel Kenya C2B IPN System

This file defines the database schema for the Airtel Kenya C2B IPN system.
The schema includes tables for transactions, validation results, and processing outcomes.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import datetime

Base = declarative_base()

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
