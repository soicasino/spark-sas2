"""
Bill Acceptor Router - Control bill acceptor operations
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from models.requests import BillAcceptorRequest
from models.responses import BillAcceptorResponse, ErrorResponse
from sas_web_service import SASWebService

router = APIRouter(prefix="/api/bill-acceptor", tags=["Bill Acceptor"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    from main import sas_service
    return sas_service


@router.post("/enable", response_model=BillAcceptorResponse)
async def enable_bill_acceptor(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Enable the bill acceptor to start accepting bills
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "bill_acceptor_enable",
            timeout=5.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return BillAcceptorResponse(
                success=True,
                message="Bill acceptor enabled successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enable bill acceptor: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bill acceptor enable error: {str(e)}"
        )


@router.post("/disable", response_model=BillAcceptorResponse)
async def disable_bill_acceptor(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Disable the bill acceptor to stop accepting bills
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "bill_acceptor_disable",
            timeout=5.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return BillAcceptorResponse(
                success=True,
                message="Bill acceptor disabled successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to disable bill acceptor: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bill acceptor disable error: {str(e)}"
        )


@router.post("/control", response_model=BillAcceptorResponse)
async def control_bill_acceptor(
    request: BillAcceptorRequest,
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Control bill acceptor with specific action
    
    - **action**: "enable", "disable", "start", "stop", "stack", or "return"
      - "enable"/"start": Enable bill acceptor to accept bills
      - "disable"/"stop": Disable bill acceptor 
      - "stack": Stack bill that is currently escrowed
      - "return": Reject/return bill that is currently escrowed
    """
    try:
        start_time = datetime.now()
        
        # Validate action
        valid_actions = ["enable", "disable", "start", "stop", "stack", "return"]
        if request.action.lower() not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Action must be one of: {', '.join(valid_actions)}"
            )
        
        # Map action to command
        action = request.action.lower()
        
        # Map frontend actions to backend commands
        command_mapping = {
            "enable": "bill_acceptor_enable",
            "disable": "bill_acceptor_disable", 
            "start": "bill_acceptor_enable",    # "start" maps to enable
            "stop": "bill_acceptor_disable",    # "stop" maps to disable
            "stack": "bill_acceptor_stack",     # Stack bill
            "return": "bill_acceptor_reject"    # "return" maps to reject
        }
        
        command_type = command_mapping.get(action, f"bill_acceptor_{action}")
        
        result = await sas_service.execute_command_async(
            command_type,
            timeout=5.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return BillAcceptorResponse(
                success=True,
                message=f"Bill acceptor {request.action.lower()}d successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to {request.action.lower()} bill acceptor: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bill acceptor control error: {str(e)}"
        )


@router.get("/status")
async def get_bill_acceptor_status(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Get current status of the bill acceptor
    """
    try:
        # Check if bill acceptor is available and get its status
        bill_acceptor_info = {
            "available": False,
            "enabled": False,
            "last_command_time": None,
            "type_id": None
        }
        
        if (sas_service.slot_machine_app and 
            sas_service.slot_machine_app.sas_comm and
            hasattr(sas_service.slot_machine_app.sas_comm, 'bill_acceptor')):
            
            bill_acceptor = sas_service.slot_machine_app.sas_comm.bill_acceptor
            
            bill_acceptor_info.update({
                "available": True,
                "enabled": getattr(bill_acceptor, 'is_billacceptor_open', 0) == 1,
                "last_command_time": getattr(bill_acceptor, 'g_last_bill_acceptor_ackapa_command', None),
                "type_id": getattr(bill_acceptor, 'g_machine_bill_acceptor_type_id', None),
                "pooling_started": getattr(bill_acceptor, 'is_bill_acceptor_pooling_started', 0) == 1
            })
            
            # Convert datetime to ISO string if present
            if bill_acceptor_info["last_command_time"]:
                bill_acceptor_info["last_command_time"] = bill_acceptor_info["last_command_time"].isoformat()
        
        return {
            "success": True,
            "message": "Bill acceptor status retrieved",
            "timestamp": datetime.now().isoformat(),
            "data": bill_acceptor_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bill acceptor status error: {str(e)}"
        )


@router.post("/reset")
async def reset_bill_acceptor(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Reset the bill acceptor
    """
    try:
        # Check if bill acceptor is available
        if not (sas_service.slot_machine_app and 
                sas_service.slot_machine_app.sas_comm and
                hasattr(sas_service.slot_machine_app.sas_comm, 'bill_acceptor')):
            raise HTTPException(
                status_code=404,
                detail="Bill acceptor not available"
            )
        
        # Call reset function directly since it's not in the command router
        sas_service.slot_machine_app.sas_comm.bill_acceptor.bill_acceptor_reset()
        
        return {
            "success": True,
            "message": "Bill acceptor reset command sent",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "action": "reset",
                "status": "completed"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bill acceptor reset error: {str(e)}"
        ) 