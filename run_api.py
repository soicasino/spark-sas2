#!/usr/bin/env python3
"""
SAS FastAPI Server Launcher
Simple script to start the FastAPI server with production-ready settings
"""
import uvicorn
import sys
import os

def main():
    """Main function to start the FastAPI server"""
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print("Starting SAS FastAPI Server...")
    print("=" * 50)
    print("API Documentation will be available at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("  - API Overview: http://localhost:8000/api")
    print("  - Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Configuration
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Set to False in production
        "log_level": "info",
        "access_log": True,
    }
    
    # Check if running in production mode
    if "--production" in sys.argv:
        config.update({
            "reload": False,
            "workers": 1,  # Adjust based on your needs
        })
        print("Running in PRODUCTION mode")
    else:
        print("Running in DEVELOPMENT mode (auto-reload enabled)")
    
    print(f"Server starting on http://{config['host']}:{config['port']}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 