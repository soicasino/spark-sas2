"""
Main FastAPI Application for SAS Slot Machine Communication
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from sas_web_service import SASWebService
from routers import system_status, meters, bill_acceptor, machine_control, websocket_routes, card_reader, ip_management, event_management
from websocket_manager import connection_manager
from routers.websocket_routes import broadcast_sas_updates
from database.db_manager import db_manager
from services.event_service import event_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global SAS service instance
sas_service: SASWebService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown
    """
    global sas_service
    
    # Startup
    logger.info("Starting SAS FastAPI application...")
    
    try:
        # Initialize database first
        logger.info("Initializing database...")
        # Database is initialized automatically when db_manager is imported
        logger.info("Database initialized successfully")
        
        # Initialize event service 
        logger.info("Event service initialized and background sync started")
        
        # Initialize SAS service
        sas_service = SASWebService()
        
        # Initialize SAS communication in background
        logger.info("Initializing SAS communication...")
        initialization_success = await sas_service.initialize()
        
        if initialization_success:
            logger.info("SAS service initialized successfully")
        else:
            logger.warning("SAS service initialization failed - running in limited mode")
        
        # Start WebSocket background broadcasting
        logger.info("Starting WebSocket broadcasting service...")
        broadcast_task = asyncio.create_task(broadcast_sas_updates(sas_service))
        logger.info("WebSocket broadcasting started")
            
    except Exception as e:
        logger.error(f"Failed to initialize SAS service: {e}")
        # Don't fail the startup - allow the API to run in limited mode
        
    yield
    
    # Shutdown
    logger.info("Shutting down SAS FastAPI application...")
    
    if sas_service:
        try:
            sas_service.shutdown()
            logger.info("SAS service shutdown completed")
        except Exception as e:
            logger.error(f"Error during SAS service shutdown: {e}")


# Create FastAPI application with lifespan management
app = FastAPI(
    title="SAS Slot Machine API",
    description="REST API for SAS (Slot Accounting System) communication with slot machines",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for Next.js integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://10.0.0.200:3000",  # Pi's own IP
        "http://10.0.0.200:3001",  # Pi's own IP alternate port
        "*"  # Allow all origins during development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "error_code": "INTERNAL_ERROR",
            "details": {
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }
        }
    )


# Include routers
# IP-based access control - no authentication needed
app.include_router(websocket_routes.router)  # WebSocket endpoints
app.include_router(system_status.router)
app.include_router(meters.router)
app.include_router(bill_acceptor.router)
app.include_router(machine_control.router)
app.include_router(card_reader.router)  # Card reader endpoints
app.include_router(ip_management.router)  # IP access control management
app.include_router(event_management.router)  # Event management and sync status


@app.get("/")
async def root():
    """
    Root endpoint - API information and status
    """
    global sas_service
    
    api_info = {
        "name": "SAS Slot Machine API",
        "version": "1.0.0",
        "description": "REST API for SAS communication with slot machines",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/system/health",
            "status": "/api/system/status"
        }
    }
    
    if sas_service:
        api_info["sas_service"] = {
            "initialized": sas_service.is_initialized,
            "running": sas_service.web_service_running,
            "connected": sas_service.system_status.get("sas_connected", False)
        }
    else:
        api_info["sas_service"] = {
            "initialized": False,
            "running": False,
            "connected": False,
            "error": "SAS service not available"
        }
    
    return api_info


@app.get("/api")
async def api_overview():
    """
    API overview with available endpoints
    """
    return {
        "success": True,
        "message": "SAS Slot Machine API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "access_control": {
                "my_ip": "GET /api/access/my-ip",
                "allowed_ips": "GET /api/access/allowed-ips",
                "add_ip": "POST /api/access/allowed-ips",
                "remove_ip": "DELETE /api/access/allowed-ips/{ip}"
            },
            "websocket": {
                "live_updates": "WS /ws/live-updates",
                "info": "GET /ws/info"
            },
            "system": {
                "status": "GET /api/system/status",
                "health": "GET /api/system/health", 
                "asset_number": "GET /api/system/asset-number",
                "sas_version": "GET /api/system/sas-version",
                "ports": "GET /api/system/ports"
            },
            "meters": {
                "all": "GET /api/meters/all?meter_type=basic&game_id=1",
                "basic": "GET /api/meters/basic",
                "extended": "GET /api/meters/extended",
                "balance": "GET /api/meters/balance",
                "request": "POST /api/meters/request"
            },
            "bill_acceptor": {
                "enable": "POST /api/bill-acceptor/enable",
                "disable": "POST /api/bill-acceptor/disable",
                "control": "POST /api/bill-acceptor/control",
                "status": "GET /api/bill-acceptor/status",
                "reset": "POST /api/bill-acceptor/reset"
            },
            "card_reader": {
                "status": "GET /api/card-reader/status",
                "eject": "POST /api/card-reader/eject",
                "last_card": "GET /api/card-reader/last-card"
            },
            "machine": {
                "lock": "POST /api/machine/lock",
                "unlock": "POST /api/machine/unlock",
                "control": "POST /api/machine/control",
                "status": "GET /api/machine/status",
                "restart": "POST /api/machine/restart",
                "emergency_stop": "POST /api/machine/emergency-stop"
            },
            "events": {
                "stats": "GET /api/events/stats",
                "unsynced": "GET /api/events/unsynced?event_type=game&limit=100",
                "sync_status": "GET /api/events/sync-status",
                "force_sync": "POST /api/events/force-sync",
                "test_connection": "POST /api/events/test-nextjs-connection",
                "cleanup": "POST /api/events/cleanup-old-events?days_old=7",
                "test_game": "POST /api/events/test-game-event?event_type=test_game_started",
                "test_card": "POST /api/events/test-card-event?event_type=card_inserted"
            }
        }
    }


# Health check endpoint (also available at /api/system/health)
@app.get("/health")
async def health_check():
    """
    Simple health check for load balancers
    """
    global sas_service
    
    if not sas_service:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "SAS service not initialized",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    is_healthy = (
        sas_service.is_initialized and 
        sas_service.web_service_running
    )
    
    status_code = 200 if is_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service_info": {
                "initialized": sas_service.is_initialized,
                "running": sas_service.web_service_running,
                "sas_connected": sas_service.system_status.get("sas_connected", False)
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    logger.info("Starting SAS FastAPI server...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 