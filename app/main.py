"""
Main application for enhanced Airtel Kenya C2B IPN system.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.api.auth import router as auth_router
from app.database import init_db
from app.utils.logger import setup_logger
from app.utils.security import get_current_active_user

# Set up logger
logger = setup_logger("main")

# Create FastAPI application with root_path
app = FastAPI(
    title="Airtel Kenya C2B IPN API",
    description="API for handling Airtel Kenya C2B Instant Payment Notifications",
    version="1.0.0",
    root_path="/airtel/c2b"  # Add this line to set the base path
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(
    api_router, 
    prefix="/api", 
    dependencies=[Depends(get_current_active_user)]  # Secure all API routes
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Airtel Kenya C2B IPN API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
