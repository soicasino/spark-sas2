"""
Pydantic response models for SAS FastAPI endpoints
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    PENDING = "pending"


class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Human-readable message about the operation")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class SystemStatusResponse(BaseResponse):
    """Response model for system status"""
    data: Dict[str, Any] = Field(description="System status information")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "System status retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 150.5,
                "data": {
                    "sas_connected": True,
                    "last_communication": "2024-01-15T10:29:45Z",
                    "asset_number": "12345678",
                    "sas_version": "6.03",
                    "port_info": "/dev/ttyUSB0",
                    "service_running": True,
                    "initialized": True
                }
            }
        }


class MetersResponse(BaseResponse):
    """Response model for meter data"""
    data: Dict[str, Any] = Field(description="Meter information")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Meters retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 2000.0,
                "data": {
                    "meter_type": "basic",
                    "status": "completed",
                    "values": {
                        "total_turnover": 15420.50,
                        "total_win": 14280.25,
                        "games_played": 1542,
                        "current_credits": 125.75
                    }
                }
            }
        }


class BalanceResponse(BaseResponse):
    """Response model for balance information"""
    data: Dict[str, float] = Field(description="Balance amounts")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Balance retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 1000.0,
                "data": {
                    "cashable_amount": 125.75,
                    "restricted_amount": 0.00,
                    "nonrestricted_amount": 50.25
                }
            }
        }


class MachineControlResponse(BaseResponse):
    """Response model for machine control operations"""
    data: Dict[str, str] = Field(description="Control operation result")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Machine control operation completed",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 500.0,
                "data": {
                    "action": "lock",
                    "status": "completed"
                }
            }
        }


class BillAcceptorResponse(BaseResponse):
    """Response model for bill acceptor operations"""
    data: Dict[str, str] = Field(description="Bill acceptor operation result")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Bill acceptor operation completed",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 300.0,
                "data": {
                    "action": "enabled",
                    "status": "completed"
                }
            }
        }


class SASVersionResponse(BaseResponse):
    """Response model for SAS version"""
    data: Dict[str, Any] = Field(description="SAS version information")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "SAS version request sent",
                "timestamp": "2024-01-15T10:30:00Z", 
                "execution_time_ms": 800.0,
                "data": {
                    "command_sent": True,
                    "version": "6.03"
                }
            }
        }


class AssetNumberResponse(BaseResponse):
    """Response model for asset number"""
    data: Dict[str, Any] = Field(description="Asset number information")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Asset number request sent",
                "timestamp": "2024-01-15T10:30:00Z",
                "execution_time_ms": 750.0,
                "data": {
                    "command_sent": True,
                    "asset_number": "12345678"
                }
            }
        }


class ErrorResponse(BaseResponse):
    """Response model for errors"""
    success: bool = False
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "SAS communication error",
                "timestamp": "2024-01-15T10:30:00Z",
                "error_code": "SAS_COMM_ERROR",
                "details": {
                    "error_type": "timeout",
                    "command": "get_balance",
                    "retry_count": 3
                }
            }
        }


class CardReaderStatusResponse(BaseModel):
    success: bool
    card_inserted: bool
    card_number: Optional[str] = None
    port_name: Optional[str] = None
    reader_connected: bool
    formatted_display: Dict[str, str]
    error_code: Optional[str] = None
    message: Optional[str] = None
    timestamp: str


class CardEventResponse(BaseModel):
    success: bool
    event_type: str  # "card_inserted" or "card_removed"
    card_number: Optional[str] = None
    formatted_display: Dict[str, str]
    error_code: Optional[str] = None
    message: Optional[str] = None
    timestamp: str 