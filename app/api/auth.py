"""
Authentication API endpoints for Airtel Kenya C2B IPN system.
"""
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.security import (
    authenticate_user, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user
)
from app.models.user import User

router = APIRouter()

@router.post("/token", response_model=Dict[str, Any])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get an access token for authentication.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Form data with username and password
        db (Session): Database session
        
    Returns:
        Dict[str, Any]: Access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=Dict[str, Any])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        Dict[str, Any]: User information
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }
