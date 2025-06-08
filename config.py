"""
Configuration settings for SAS FastAPI application
"""
import os
from typing import List

class Settings:
    """Application settings"""
    
    # API Settings
    API_TITLE = "SAS Slot Machine API"
    API_VERSION = "1.0.0" 
    API_DESCRIPTION = "REST API for SAS (Slot Accounting System) communication with slot machines"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings  
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js development
        "http://localhost:3001",  # Next.js alternative port
        "http://127.0.0.1:3000",
        # Add production URLs as needed
    ]
    
    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # WebSocket Settings
    WEBSOCKET_BROADCAST_INTERVAL: int = 5  # seconds
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # SAS Settings
    SAS_COMMAND_TIMEOUT: float = 10.0  # seconds
    SAS_RECONNECT_ATTEMPTS: int = 3
    SAS_RECONNECT_DELAY: int = 5  # seconds
    
    # Default user credentials (change in production!)
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "admin")
    DEFAULT_PASSWORD: str = os.getenv("DEFAULT_PASSWORD", "admin123")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100  # requests per minute
    RATE_LIMIT_WINDOW: int = 60  # seconds

# Global settings instance
settings = Settings() 