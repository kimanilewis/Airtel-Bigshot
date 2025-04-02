"""
Database connection utilities for the Airtel Kenya C2B IPN system.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import DB_URL

# Create SQLAlchemy engine
engine = create_engine(DB_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Base class for all models
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """
    Initialize the database by creating all tables.
    """
    # Import all models to ensure they are registered with Base
    from app.models.transaction import Transaction
    from app.models.validation import ValidationResult
    from app.models.processing import ProcessingResult
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
