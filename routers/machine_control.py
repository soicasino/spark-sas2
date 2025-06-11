"""
Machine Control Router - Handle machine lock/unlock and control operations
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from models.requests import MachineControlRequest
from models.responses import MachineControlResponse, ErrorResponse
from sas_web_service import SASWebService

router = APIRouter(prefix="/api/machine", tags=["Machine Control"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    from main import sas_service
    return sas_service


@router.post("/lock", response_model=MachineControlResponse)
async def lock_machine(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Lock the slot machine to prevent gameplay
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "machine_lock",
            timeout=10.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MachineControlResponse(
                success=True,
                message="Machine locked successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to lock machine: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Machine lock error: {str(e)}"
        )


@router.post("/unlock", response_model=MachineControlResponse)
async def unlock_machine(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Unlock the slot machine to allow gameplay
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "machine_unlock",
            timeout=10.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MachineControlResponse(
                success=True,
                message="Machine unlocked successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to unlock machine: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Machine unlock error: {str(e)}"
        )


@router.post("/control", response_model=MachineControlResponse)
async def control_machine(
    request: MachineControlRequest,
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Control machine with specific action
    
    - **action**: "lock", "unlock", or "restart"
    - **lock_code**: Lock code for machine operations (default: "00")
    - **timeout**: Timeout for the operation in BCD format (default: 9000)
    """
    try:
        start_time = datetime.now()
        
        # Validate action
        valid_actions = ["lock", "unlock", "restart", "add_credits", "subtract_credits"]
        if request.action.lower() not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Action must be one of: {', '.join(valid_actions)}"
            )
        
        # Handle credit operations differently
        if request.action.lower() in ["add_credits", "subtract_credits"]:
            # Handle credit transfer operations
            try:
                amount = request.amount if request.amount else 0
                if amount <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Amount must be greater than 0 for credit operations"
                    )
                
                # Convert to credits (assuming amount is in dollars, multiply by 100 for cents)
                credits = int(amount * 100)
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if request.action.lower() == "add_credits":
                    # Implement actual AFT credit transfer
                    if (sas_service.slot_machine_app and 
                        sas_service.slot_machine_app.sas_comm and 
                        sas_service.slot_machine_app.sas_comm.sas_money):
                        
                        sas_comm = sas_service.slot_machine_app.sas_comm
                        
                        # AFT parameters - using defaults from working code
                        doincreasetransactionid = 1
                        transfertype = 0  # Cashable transfer (00)
                        customerbalance = amount  # Amount in dollars
                        customerpromo = 0  # No promotional amount
                        transactionid = int(datetime.now().timestamp())  # Generate unique transaction ID
                        assetnumber = sas_comm.sas_address  # SAS address
                        registrationkey = "0000"  # Default registration key
                        
                        # Execute AFT credit transfer
                        try:
                            result = sas_comm.money_cash_in(
                                doincreasetransactionid,
                                transfertype,
                                customerbalance,
                                customerpromo,
                                transactionid,
                                assetnumber,
                                registrationkey
                            )
                            
                            return MachineControlResponse(
                                success=True,
                                message=f"Credit addition of ${amount:.2f} initiated successfully",
                                execution_time_ms=execution_time,
                                data={
                                    "action": "add_credits", 
                                    "amount": amount, 
                                    "credits": credits,
                                    "transaction_id": transactionid,
                                    "transfer_type": "cashable"
                                }
                            )
                        except Exception as aft_error:
                            raise HTTPException(
                                status_code=500,
                                detail=f"AFT credit transfer failed: {str(aft_error)}"
                            )
                    else:
                        raise HTTPException(
                            status_code=503,
                            detail="SAS communication not available for credit transfer"
                        )
                        
                else:  # subtract_credits
                    # Implement actual AFT cashout
                    if (sas_service.slot_machine_app and 
                        sas_service.slot_machine_app.sas_comm and 
                        sas_service.slot_machine_app.sas_comm.sas_money):
                        
                        sas_comm = sas_service.slot_machine_app.sas_comm
                        
                        # AFT cashout parameters
                        doincreaseid = 1
                        transactionid = int(datetime.now().timestamp())
                        assetnumber = sas_comm.sas_address
                        registrationkey = "0000"
                        
                        try:
                            result = sas_comm.money_cash_out(
                                doincreaseid,
                                transactionid,
                                assetnumber,
                                registrationkey
                            )
                            
                            return MachineControlResponse(
                                success=True,
                                message=f"Credit subtraction initiated successfully",
                                execution_time_ms=execution_time,
                                data={
                                    "action": "subtract_credits", 
                                    "amount": amount, 
                                    "credits": credits,
                                    "transaction_id": transactionid,
                                    "transfer_type": "cashout"
                                }
                            )
                        except Exception as aft_error:
                            raise HTTPException(
                                status_code=500,
                                detail=f"AFT cashout failed: {str(aft_error)}"
                            )
                    else:
                        raise HTTPException(
                            status_code=503,
                            detail="SAS communication not available for cashout"
                        )
                    
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Credit operation error: {str(e)}"
                )
        
        # Map action to command for lock/unlock/restart
        command_type = f"machine_{request.action.lower()}"
        
        # Prepare parameters
        parameters = {
            "lock_code": request.lock_code,
            "timeout": request.timeout
        }
        
        result = await sas_service.execute_command_async(
            command_type,
            parameters=parameters,
            timeout=15.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MachineControlResponse(
                success=True,
                message=f"Machine {request.action.lower()} completed successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to {request.action.lower()} machine: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Machine control error: {str(e)}"
        )


@router.get("/status")
async def get_machine_status(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Get current machine status and state information
    """
    try:
        # Get basic machine status
        machine_info = {
            "sas_connected": False,
            "initialized": False,
            "running": False,
            "last_poll_type": None,
            "device_type_id": None,
            "port_name": None,
            "communication_active": False
        }
        
        if (sas_service.slot_machine_app and 
            sas_service.slot_machine_app.sas_comm):
            
            sas_comm = sas_service.slot_machine_app.sas_comm
            
            machine_info.update({
                "sas_connected": sas_comm.is_port_open,
                "initialized": sas_service.is_initialized,
                "running": sas_service.slot_machine_app.running,
                "last_poll_type": getattr(sas_comm, 'last_sent_poll_type', None),
                "device_type_id": getattr(sas_comm, 'device_type_id', None),
                "port_name": getattr(sas_comm, 'port_name', None),
                "communication_active": sas_service.web_service_running,
                "sas_address": getattr(sas_comm, 'sas_address', None)
            })
        
        return {
            "success": True,
            "message": "Machine status retrieved",
            "timestamp": datetime.now().isoformat(),
            "data": machine_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Machine status error: {str(e)}"
        )


@router.post("/restart")
async def restart_machine(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Restart the slot machine (software restart)
    
    Note: This is a placeholder implementation. The actual restart command
    depends on your specific slot machine's SAS implementation.
    """
    try:
        start_time = datetime.now()
        
        # This is a placeholder - you'll need to implement the actual SAS restart command
        # Different machines may have different restart procedures
        
        result = await sas_service.execute_command_async(
            "machine_restart",
            timeout=30.0  # Restart might take longer
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MachineControlResponse(
                success=True,
                message="Machine restart initiated successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart machine: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Machine restart error: {str(e)}"
        )


@router.post("/emergency-stop")
async def emergency_stop_machine(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Emergency stop - immediately halt all machine operations
    
    This is for emergency situations and will stop the SAS communication loop.
    """
    try:
        # Stop the slot machine application
        if sas_service.slot_machine_app:
            sas_service.slot_machine_app.running = False
            
        return {
            "success": True,
            "message": "Emergency stop executed - machine operations halted",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "action": "emergency_stop",
                "status": "completed",
                "warning": "SAS communication has been stopped. System restart may be required."
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Emergency stop error: {str(e)}"
        ) 