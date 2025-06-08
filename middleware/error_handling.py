"""
Enhanced Error Handling Middleware
Provides structured error responses with proper logging and error codes
"""
import logging
import traceback
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorCode:
    """Standardized error codes"""
    # Authentication
    AUTHENTICATION_FAILED = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002" 
    TOKEN_INVALID = "AUTH_003"
    INSUFFICIENT_PERMISSIONS = "AUTH_004"
    
    # SAS Communication
    SAS_NOT_INITIALIZED = "SAS_001"
    SAS_COMMUNICATION_FAILED = "SAS_002"
    SAS_COMMAND_TIMEOUT = "SAS_003"
    SAS_INVALID_RESPONSE = "SAS_004"
    
    # API Validation
    VALIDATION_ERROR = "API_001"
    INVALID_REQUEST = "API_002"
    MISSING_PARAMETER = "API_003"
    
    # System Errors
    INTERNAL_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    RATE_LIMIT_EXCEEDED = "SYS_003"
    
    # WebSocket
    WEBSOCKET_CONNECTION_FAILED = "WS_001"
    WEBSOCKET_AUTH_FAILED = "WS_002"

class SASError(Exception):
    """Custom exception for SAS-related errors"""
    def __init__(self, message: str, error_code: str = ErrorCode.SAS_COMMUNICATION_FAILED, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message: str, error_code: str = ErrorCode.AUTHENTICATION_FAILED, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def create_error_response(
    status_code: int,
    message: str,
    error_code: str,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Create standardized error response"""
    
    error_response = {
        "success": False,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "error_code": error_code,
    }
    
    if details:
        error_response["details"] = details
        
    if request_id:
        error_response["request_id"] = request_id
        
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

async def sas_error_handler(request: Request, exc: SASError) -> JSONResponse:
    """Handle SAS-specific errors"""
    logger.error(f"SAS Error: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "path": request.url.path
    })
    
    return create_error_response(
        status_code=503,  # Service Unavailable
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )

async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors"""
    logger.warning(f"Authentication Error: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown"
    })
    
    return create_error_response(
        status_code=401,  # Unauthorized
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation Error: {exc}", extra={
        "path": request.url.path,
        "errors": exc.errors()
    })
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        status_code=422,  # Unprocessable Entity
        message="Request validation failed",
        error_code=ErrorCode.VALIDATION_ERROR,
        details={
            "validation_errors": formatted_errors
        }
    )

async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Error {exc.status_code}: {exc.detail}", extra={
        "path": request.url.path,
        "status_code": exc.status_code
    })
    
    error_code_map = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.AUTHENTICATION_FAILED,
        403: ErrorCode.INSUFFICIENT_PERMISSIONS,
        404: "NOT_FOUND",
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE
    }
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=error_code_map.get(exc.status_code, "HTTP_ERROR")
    )

async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={
        "path": request.url.path,
        "traceback": traceback.format_exc()
    })
    
    # Don't expose internal error details in production
    from config import settings
    if settings.DEBUG:
        details = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc()
        }
    else:
        details = {
            "error_type": type(exc).__name__
        }
    
    return create_error_response(
        status_code=500,
        message="Internal server error",
        error_code=ErrorCode.INTERNAL_ERROR,
        details=details
    ) 