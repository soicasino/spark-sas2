"""
System Status Router - Health checks, port status, and system information
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from typing import Dict, Any

from models.responses import SystemStatusResponse, AssetNumberResponse, SASVersionResponse, ErrorResponse
from sas_web_service import SASWebService
from middleware.ip_access_control import verify_ip_access

router = APIRouter(prefix="/api/system", tags=["System Status"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    # This will be injected from the main app
    from main import sas_service
    if sas_service is None:
        raise HTTPException(
            status_code=503,
            detail="SAS service not available - service may be starting up or failed to initialize"
        )
    return sas_service


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    sas_service: SASWebService = Depends(get_sas_service),
    client_ip: str = Depends(verify_ip_access)
):
    """
    Get comprehensive system status including SAS connection, port info, and service health
    """
    try:
        start_time = datetime.now()
        
        # Execute system status command
        result = await sas_service.execute_command_async("system_status", timeout=5.0)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return SystemStatusResponse(
                success=True,
                message="System status retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get system status: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"System status error: {str(e)}"
        )


@router.get("/basic-status")
async def get_basic_status(client_ip: str = Depends(verify_ip_access)):
    """
    Get basic system status without requiring full SAS service initialization
    This endpoint works even when SAS service is not available
    """
    try:
        from main import sas_service
        
        basic_status = {
            "api_running": True,
            "timestamp": datetime.now().isoformat(),
            "sas_service_available": sas_service is not None,
        }
        
        if sas_service is not None:
            basic_status.update({
                "sas_initialized": sas_service.is_initialized,
                "sas_running": sas_service.web_service_running,
                "sas_connected": sas_service.system_status.get("sas_connected", False),
                "last_communication": sas_service.system_status.get("last_communication"),
                "port_info": sas_service.system_status.get("port_info"),
                "asset_number": sas_service.system_status.get("asset_number")
            })
        else:
            basic_status.update({
                "sas_initialized": False,
                "sas_running": False,
                "sas_connected": False,
                "error": "SAS service failed to initialize"
            })
        
        return {
            "success": True,
            "message": "Basic status retrieved successfully",
            "data": basic_status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Basic status error: {str(e)}"
        )


@router.get("/health")
async def health_check(client_ip: str = Depends(verify_ip_access)):
    """
    Simple health check endpoint for load balancers and monitoring
    This endpoint works even when SAS service is not available
    """
    try:
        from main import sas_service
        
        if sas_service is None:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "initialized": False,
                "service_running": False,
                "sas_connected": False,
                "error": "SAS service not initialized"
            }
        
        is_healthy = (
            sas_service.is_initialized and 
            sas_service.web_service_running and
            sas_service.system_status.get("sas_connected", False)
        )
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "initialized": sas_service.is_initialized,
            "service_running": sas_service.web_service_running,
            "sas_connected": sas_service.system_status.get("sas_connected", False)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/asset-number", response_model=AssetNumberResponse)
async def get_asset_number(
    sas_service: SASWebService = Depends(get_sas_service),
    client_ip: str = Depends(verify_ip_access)
):
    """
    Get the slot machine asset number
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async("get_asset_number", timeout=10.0)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return AssetNumberResponse(
                success=True,
                message="Asset number request completed",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get asset number: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Asset number error: {str(e)}"
        )


@router.get("/sas-version", response_model=SASVersionResponse)
async def get_sas_version(
    sas_service: SASWebService = Depends(get_sas_service),
    client_ip: str = Depends(verify_ip_access)
):
    """
    Get the SAS protocol version from the slot machine
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async("get_sas_version", timeout=10.0)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return SASVersionResponse(
                success=True,
                message="SAS version request completed",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get SAS version: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SAS version error: {str(e)}"
        )


@router.get("/ports")
async def get_port_information(
    sas_service: SASWebService = Depends(get_sas_service),
    client_ip: str = Depends(verify_ip_access)
):
    """
    Get information about available and used ports
    """
    try:
        port_info = {}
        
        if (sas_service.slot_machine_app and 
            hasattr(sas_service.slot_machine_app, 'port_mgr')):
            
            port_mgr = sas_service.slot_machine_app.port_mgr
            
            port_info = {
                "available_ports": getattr(port_mgr, 'available_ports', []),
                "sas_port": getattr(sas_service.slot_machine_app.sas_comm, 'port_name', None) if sas_service.slot_machine_app.sas_comm else None,
                "card_reader_port": getattr(sas_service.slot_machine_app.card_reader_mgr.card_reader, 'port_name', None) if (sas_service.slot_machine_app.card_reader_mgr and sas_service.slot_machine_app.card_reader_mgr.card_reader) else None
            }
        
        return {
            "success": True,
            "message": "Port information retrieved",
            "timestamp": datetime.now().isoformat(),
            "data": port_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Port information error: {str(e)}"
        ) 