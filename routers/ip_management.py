"""
IP Management Router
Endpoints for managing IP access control whitelist
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from typing import List
from pydantic import BaseModel

from middleware.ip_access_control import ip_access_control, verify_ip_access

router = APIRouter(prefix="/api/access", tags=["IP Access Control"])

class AddIPRequest(BaseModel):
    ip_or_network: str
    description: str = ""

class IPListResponse(BaseModel):
    success: bool
    allowed_ips: List[str]
    total_count: int
    timestamp: str

@router.get("/allowed-ips", response_model=IPListResponse)
async def get_allowed_ips(client_ip: str = Depends(verify_ip_access)):
    """Get list of allowed IPs/networks"""
    try:
        allowed_ips = ip_access_control.get_allowed_ips()
        
        return IPListResponse(
            success=True,
            allowed_ips=allowed_ips,
            total_count=len(allowed_ips),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "IP_001",
                "message": f"Failed to get IP list: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/allowed-ips")
async def add_allowed_ip(
    request: AddIPRequest,
    client_ip: str = Depends(verify_ip_access)
):
    """Add an IP or network to the allowed list"""
    try:
        success = ip_access_control.add_allowed_ip(request.ip_or_network)
        
        if success:
            return {
                "success": True,
                "message": f"IP/Network added to whitelist: {request.ip_or_network}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error_code": "IP_002",
                    "message": f"Invalid IP/Network format: {request.ip_or_network}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "IP_003",
                "message": f"Failed to add IP: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.delete("/allowed-ips/{ip_or_network:path}")
async def remove_allowed_ip(
    ip_or_network: str,
    client_ip: str = Depends(verify_ip_access)
):
    """Remove an IP or network from the allowed list"""
    try:
        success = ip_access_control.remove_allowed_ip(ip_or_network)
        
        if success:
            return {
                "success": True,
                "message": f"IP/Network removed from whitelist: {ip_or_network}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error_code": "IP_004",
                    "message": f"IP/Network not found in whitelist: {ip_or_network}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "IP_005",
                "message": f"Failed to remove IP: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/my-ip")
async def get_my_ip(request: Request):
    """Get your current IP address (no IP restriction for this endpoint)"""
    try:
        from middleware.ip_access_control import get_client_ip
        client_ip = get_client_ip(request)
        is_allowed = ip_access_control.is_ip_allowed(client_ip)
        
        return {
            "success": True,
            "your_ip": client_ip,
            "is_allowed": is_allowed,
            "message": f"Your IP: {client_ip} ({'✅ Allowed' if is_allowed else '❌ Blocked'})",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "IP_006",
                "message": f"Failed to get IP info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        ) 