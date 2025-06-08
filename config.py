"""
Configuration settings for SAS API
"""
import os
from typing import Optional

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Next.js app configuration
        self.NEXTJS_BASE_URL: str = os.getenv('NEXTJS_BASE_URL', 'http://localhost:3000')
        self.NEXTJS_TIMEOUT: float = float(os.getenv('NEXTJS_TIMEOUT', '5.0'))
        
        # Database configuration
        self.DATABASE_URL: str = os.getenv('DATABASE_URL', 'sas_data.db')
        
        # API configuration
        self.API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
        self.API_PORT: int = int(os.getenv('API_PORT', '8000'))
        
        # Sync configuration
        self.SYNC_INTERVAL: int = int(os.getenv('SYNC_INTERVAL', '30'))  # seconds
        self.MAX_SYNC_RETRIES: int = int(os.getenv('MAX_SYNC_RETRIES', '3'))
        
        # Cleanup configuration
        self.CLEANUP_DAYS: int = int(os.getenv('CLEANUP_DAYS', '7'))  # days to keep synced events

# Global settings instance
settings = Settings() 