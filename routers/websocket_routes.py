"""
WebSocket Router - Real-time SAS data streaming
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from datetime import datetime
from typing import Optional

from websocket_manager import connection_manager
from auth.security import verify_token

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/live-updates")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT token for authentication")
):
    """
    WebSocket endpoint for real-time SAS data updates
    
    **Authentication:** 
    - Include JWT token in query parameter: `?token=your_jwt_token`
    - Or skip authentication for development/testing
    
    **Subscription Events:**
    - `meters`: Real-time meter updates 
    - `system_status`: SAS connection status changes
    - `machine_events`: Machine lock/unlock, game events
    - `bill_events`: Bill acceptor events
    - `heartbeat`: Periodic connection health checks
    
    **Client Messages:**
    - `{"type": "ping"}`: Ping the server
    - `{"type": "subscribe", "events": ["meters", "system_status"]}`: Update subscriptions
    - `{"type": "request_current_data"}`: Get latest data immediately
    """
    
    # Optional authentication
    user_info = {"authenticated": False}
    if token:
        token_data = verify_token(token)
        if token_data and token_data.username:
            from auth.security import get_user
            user = get_user(token_data.username)
            if user:
                user_info = {
                    "authenticated": True,
                    "username": user.username,
                    "scopes": user.scopes
                }
    
    # Accept connection
    await connection_manager.connect(websocket, user_info)
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            await connection_manager.handle_client_message(websocket, data)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)

@router.get("/connection-stats")
async def get_websocket_stats():
    """
    Get current WebSocket connection statistics
    """
    return {
        "success": True,
        "data": connection_manager.get_connection_stats(),
        "timestamp": datetime.now().isoformat()
    }

# Background task to broadcast SAS updates
async def broadcast_sas_updates(sas_service):
    """
    Background task to periodically broadcast SAS data to WebSocket clients
    """
    while True:
        try:
            # Get current meter data
            try:
                meter_result = await sas_service.execute_command("get_meters", {"meter_type": "basic"})
                if meter_result and meter_result.get("status") == "success":
                    await connection_manager.broadcast_to_subscribed("meters", meter_result)
            except Exception as e:
                print(f"Error getting meters for WebSocket broadcast: {e}")
            
            # Get system status
            try:
                status_result = await sas_service.execute_command("system_status", {})
                if status_result:
                    await connection_manager.broadcast_to_subscribed("system_status", status_result)
            except Exception as e:
                print(f"Error getting system status for WebSocket broadcast: {e}")
            
            # Wait before next update
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in WebSocket broadcast loop: {e}")
            await asyncio.sleep(5)  # Wait before retrying 