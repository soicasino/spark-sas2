from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from models.responses import CardReaderStatusResponse, CardEventResponse, ErrorResponse
from sas_web_service import SASWebService
from middleware.ip_access_control import verify_ip_access
from websocket_manager import connection_manager
import asyncio

router = APIRouter(prefix="/api/card-reader", tags=["Card Reader"])

# Shared SAS service instance
sas_service = SASWebService()

@router.get("/status", response_model=CardReaderStatusResponse)
async def get_card_reader_status(client_ip: str = Depends(verify_ip_access)):
    """Get current card reader status and card information."""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, sas_service.get_card_reader_status
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": result.get("error_code", "SAS_008"),
                    "message": result.get("message", "Card reader operation failed"),
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        formatted_display = {
            "card_status": f"🟢 Card Inserted" if result.get("card_inserted") else "🔴 No Card",
            "card_number": result.get("card_number") or "None",
            "reader_status": f"🟢 Connected" if result.get("reader_connected") else "🔴 Disconnected", 
            "port_name": result.get("port_name") or "Not configured"
        }
        
        return CardReaderStatusResponse(
            success=True,
            card_inserted=result.get("card_inserted", False),
            card_number=result.get("card_number"),
            port_name=result.get("port_name"),
            reader_connected=result.get("reader_connected", False),
            formatted_display=formatted_display,
            message="Card reader status retrieved successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "API_008",
                "message": f"Failed to get card reader status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/eject")
async def eject_card(client_ip: str = Depends(verify_ip_access)):
    """Send eject command to remove inserted card."""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, sas_service.eject_card
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": result.get("error_code", "SAS_009"),
                    "message": result.get("message", "Card eject operation failed"),
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        formatted_display = {
            "action": "🚀 Card Eject",
            "status": "✅ Command Sent",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # Broadcast card eject event
        await connection_manager.broadcast_to_subscribed("card_events", {
            "event_type": "card_ejected",
            "formatted_display": formatted_display,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Card eject command sent successfully",
            "formatted_display": formatted_display,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "API_009",
                "message": f"Failed to eject card: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/last-card")
async def get_last_card(client_ip: str = Depends(verify_ip_access)):
    """Get information about the last detected card."""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, sas_service.get_last_card_info
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": result.get("error_code", "SAS_010"),
                    "message": result.get("message", "Last card info operation failed"),
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        formatted_display = {
            "last_card": result.get("last_card_number", "None"),
            "card_history": f"Last seen: {result.get('last_card_number', 'None')}",
            "reader_status": f"🟢 Active" if result.get("reader_connected") else "🔴 Inactive"
        }
        
        return {
            "success": True,
            "last_card_number": result.get("last_card_number"),
            "reader_connected": result.get("reader_connected", False),
            "port_name": result.get("port_name"),
            "formatted_display": formatted_display,
            "message": "Last card information retrieved successfully", 
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "API_010",
                "message": f"Failed to get last card info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        ) 