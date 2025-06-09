"""
Pydantic request models for SAS FastAPI endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class MeterType(str, Enum):
    BASIC = "basic"
    EXTENDED = "extended"
    ALL = "all"
    BILL = "bill"
    GAME = "game"


class TransferType(str, Enum):
    CASHABLE = "10"
    RESTRICTED = "11"
    NONRESTRICTED = "00"


class MeterRequest(BaseModel):
    """Request model for meter operations"""
    meter_type: MeterType = Field(MeterType.BASIC, description="Type of meters to retrieve")
    game_id: Optional[int] = Field(None, description="Game ID for game-specific meters")
    
    class Config:
        schema_extra = {
            "example": {
                "meter_type": "basic",
                "game_id": None
            }
        }


class MoneyTransferRequest(BaseModel):
    """Request model for money transfer operations"""
    transfer_type: TransferType = Field(description="Type of transfer")
    amount: float = Field(gt=0, description="Amount to transfer (must be positive)")
    transaction_id: Optional[str] = Field(None, description="Custom transaction ID")
    
    class Config:
        schema_extra = {
            "example": {
                "transfer_type": "10",
                "amount": 100.50,
                "transaction_id": "TXN123456"
            }
        }


class BillAcceptorRequest(BaseModel):
    """Request model for bill acceptor operations"""
    action: str = Field(description="Action to perform: 'enable' or 'disable'")
    
    class Config:
        schema_extra = {
            "example": {
                "action": "enable"
            }
        }


class MachineControlRequest(BaseModel):
    """Request model for machine control operations"""
    action: str = Field(description="Action to perform: 'lock', 'unlock', 'restart', 'add_credits', or 'subtract_credits'")
    lock_code: Optional[str] = Field("00", description="Lock code for machine operations")
    timeout: Optional[int] = Field(9000, description="Timeout for the operation in BCD format")
    amount: Optional[float] = Field(None, description="Amount for credit operations (required for add_credits/subtract_credits)")
    
    class Config:
        schema_extra = {
            "example": {
                "action": "lock",
                "lock_code": "00",
                "timeout": 9000,
                "amount": 25.50
            }
        }


class CashoutRequest(BaseModel):
    """Request model for cashout operations"""
    amount: Optional[float] = Field(None, description="Specific amount to cashout (if None, cashout all)")
    transaction_id: Optional[str] = Field(None, description="Custom transaction ID")
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 125.75,
                "transaction_id": "CASHOUT123"
            }
        }


class CardReaderRequest(BaseModel):
    """Request model for card reader operations"""
    action: str = Field(description="Action to perform: 'eject', 'status', or 'led_color'")
    color_command: Optional[str] = Field(None, description="Hex command for LED color (if action is 'led_color')")
    
    class Config:
        schema_extra = {
            "example": {
                "action": "eject",
                "color_command": None
            }
        } 