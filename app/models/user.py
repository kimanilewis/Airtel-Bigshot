"""
User model for JWT authentication in Airtel Kenya C2B IPN system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime

from app.database import Base


class User(Base):
    """
    Stores API users for JWT authentication.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
