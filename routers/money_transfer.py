"""
Money Transfer Router - Handle AFT (Advanced Funds Transfer) operations
Based on para_commands.py.ref implementation for SAS protocol
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from decimal import Decimal
import asyncio

from models.requests import MoneyTransferRequest, CashoutRequest
from models.responses import MachineControlResponse, ErrorResponse
from sas_web_service import SASWebService

# Import WebSocket manager for real-time events
try:
    from websocket_manager import connection_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️ WebSocket manager not available for money transfer events")

router = APIRouter(prefix="/api/money", tags=["Money Transfer"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    from main import sas_service
    return sas_service


async def broadcast_money_event(event_type: str, data: dict):
    """Broadcast money transfer event to WebSocket clients"""
    if WEBSOCKET_AVAILABLE:
        try:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            await connection_manager.broadcast_to_subscribed("money_events", event_data)
            print(f"📡 Money event broadcasted via WebSocket: {event_type}")
        except Exception as e:
            print(f"⚠️ Failed to broadcast money event via WebSocket: {e}")


@router.post("/add-credits", response_model=MachineControlResponse)
async def add_credits(
    request: MoneyTransferRequest,
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Add credits to the slot machine using AFT (Advanced Funds Transfer)
    
    - **transfer_type**: Type of transfer ("10" for cashable, "11" for restricted, "00" for non-restricted)
    - **amount**: Amount to transfer in dollars (will be converted to credits)
    - **transaction_id**: Optional custom transaction ID
    """
    try:
        start_time = datetime.now()
        
        if request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )
        
        # Check SAS communication availability
        if not (sas_service.slot_machine_app and 
                sas_service.slot_machine_app.sas_comm):
            raise HTTPException(
                status_code=503,
                detail="SAS communication not available"
            )
        
        sas_comm = sas_service.slot_machine_app.sas_comm
        
        # AFT Cash-In Parameters (based on para_commands.py.ref)
        doincreasetransactionid = 1  # Always increment transaction ID
        transfertype = int(request.transfer_type)  # 10=cashable, 11=restricted, 00=non-restricted
        customerbalance = float(request.amount)  # Amount in dollars
        customerpromo = 0.0  # No promotional amount for basic transfers
        
        # Generate transaction ID or use provided one
        if request.transaction_id:
            transactionid = int(request.transaction_id) if request.transaction_id.isdigit() else hash(request.transaction_id) % 10000
        else:
            transactionid = int(datetime.now().timestamp()) % 10000
        
        # SAS configuration parameters
        assetnumber = sas_comm.sas_address if hasattr(sas_comm, 'sas_address') else "01000000"
        registrationkey = "00000000000000000000000000000000000000000000"  # 20 bytes of zeros
        
        # Execute AFT credit loading using SAS money functions
        try:
            # Get the SAS communicator instance and money functions
            if not sas_comm or not hasattr(sas_comm, 'sas_money') or not sas_comm.sas_money:
                raise Exception("SAS money functions not available")

            sas_money = sas_comm.sas_money
            
            amount = request.amount
            transfer_type = int(request.transfer_type)
            
            if amount <= 0:
                raise Exception("Amount must be greater than 0")

            # 1. Initiate the transfer
            transaction_id = sas_money.komut_para_yukle(
                doincreasetransactionid=1,
                transfertype=transfer_type, 
                customerbalance=float(amount),
                customerpromo=0.0,
                transactionid=int(datetime.now().timestamp()) % 10000,
                assetnumber=sas_comm.sas_address,
                registrationkey="0000000000000000000000000000000000000000"
            )

            # 2. Wait for the transfer to complete
            print(f"[MoneyTransfer] Waiting for AFT completion...")
            success, message = sas_money.wait_for_aft_completion(timeout=15.0)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 3. Return the final result
            if success:
                print(f"[MoneyTransfer] AFT transfer completed successfully")
                
                # OPTIONAL: After a successful transfer, query the balance again
                # to include it in the response.
                sas_money.komut_bakiye_sorgulama("API", 0, "PostAFTBalance")
                
                # Prepare response data
                response_data = {
                    "action": "add_credits",
                    "amount": amount,
                    "credits": int(amount * 100),  # Convert to credits (cents)
                    "transaction_id": transaction_id,
                    "transfer_type": request.transfer_type,
                    "transfer_type_name": get_transfer_type_name(request.transfer_type),
                    "final_status": "COMPLETED",
                    "timestamp": datetime.now().isoformat(),
                    "status_message": message
                }
                
                # Broadcast WebSocket event for successful credit addition
                await broadcast_money_event("credits_added", {
                    "success": True,
                    "amount": amount,
                    "transfer_type": request.transfer_type,
                    "transaction_id": transaction_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return MachineControlResponse(
                    success=True,
                    message=f"Credit addition of ${amount:.2f} completed successfully",
                    execution_time_ms=execution_time,
                    data=response_data
                )
            else:
                print(f"[MoneyTransfer] AFT transfer failed: {message}")
                
                # Prepare error response data
                response_data = {
                    "action": "add_credits",
                    "amount": amount,
                    "transfer_type": transfer_type,
                    "final_status": "FAILED",
                    "error": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Broadcast WebSocket event for failed credit addition
                await broadcast_money_event("credits_failed", {
                    "success": False,
                    "amount": amount,
                    "error": message,
                    "timestamp": datetime.now().isoformat()
                })
                
                return MachineControlResponse(
                    success=False,
                    message=f"Credit addition failed: {message}",
                    execution_time_ms=execution_time,
                    data=response_data
                )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = str(e)
            print(f"[MoneyTransfer] Exception during credit addition: {error_msg}")
            
            # Broadcast WebSocket event for error
            await broadcast_money_event("credits_error", {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            
            raise HTTPException(status_code=500, detail=f"Failed to add credits: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Money transfer error: {str(e)}"
        )


@router.post("/cashout", response_model=MachineControlResponse)
async def cashout_credits(
    request: CashoutRequest,
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Cashout credits from the slot machine using AFT
    
    - **amount**: Specific amount to cashout (if None, cashout all available balance)
    - **transaction_id**: Optional custom transaction ID
    """
    try:
        start_time = datetime.now()
        
        # Check SAS communication availability
        if not (sas_service.slot_machine_app and 
                sas_service.slot_machine_app.sas_comm):
            raise HTTPException(
                status_code=503,
                detail="SAS communication not available"
            )
        
        sas_comm = sas_service.slot_machine_app.sas_comm
        
        # First query balance to check available funds
        try:
            # Query current balance using SAS money functions
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                balance_result = sas_comm.sas_money.komut_bakiye_sorgulama(
                    sender=2,  # Cashout operation
                    isforinfo=0,  # Required for operation
                    sendertext="API-Cashout"
                )
                
                # Wait briefly for balance response
                await asyncio.sleep(0.5)
                
                # Get current balance
                current_balance = sas_comm.sas_money.yanit_bakiye_tutar
                restricted_balance = sas_comm.sas_money.yanit_restricted_amount
                nonrestricted_balance = sas_comm.sas_money.yanit_nonrestricted_amount
                
                total_balance = current_balance + restricted_balance + nonrestricted_balance
                
                if total_balance <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="No balance available to cashout"
                    )
                
                # Check if requested amount is available
                if request.amount and request.amount > total_balance:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Requested amount ${request.amount:.2f} exceeds available balance ${total_balance:.2f}"
                    )
                
            else:
                raise HTTPException(
                    status_code=503,
                    detail="SAS money functions not available"
                )
        
        except Exception as balance_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query balance: {str(balance_error)}"
            )
        
        # AFT Cashout Parameters (based on para_commands.py.ref)
        doincreaseid = 1  # Always increment transaction ID
        
        # Generate transaction ID or use provided one
        if request.transaction_id:
            transactionid = int(request.transaction_id) if request.transaction_id.isdigit() else hash(request.transaction_id) % 10000
        else:
            transactionid = int(datetime.now().timestamp()) % 10000
        
        # SAS configuration parameters
        assetnumber = sas_comm.sas_address if hasattr(sas_comm, 'sas_address') else "01000000"
        registrationkey = "00000000000000000000000000000000000000000000"  # 20 bytes of zeros
        
        # Execute AFT cashout using SAS money functions
        try:
            result = sas_comm.sas_money.komut_para_sifirla(
                doincreaseid,
                transactionid,
                assetnumber,
                registrationkey
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            cashout_amount = request.amount if request.amount else total_balance
            
            # Prepare response data
            response_data = {
                "action": "cashout",
                "requested_amount": request.amount,
                "total_balance": total_balance,
                "cashable_balance": current_balance,
                "restricted_balance": restricted_balance,
                "nonrestricted_balance": nonrestricted_balance,
                "transaction_id": transactionid
            }
            
            # Broadcast WebSocket event
            await broadcast_money_event("cashout_initiated", {
                "success": True,
                "cashout_amount": cashout_amount,
                "requested_amount": request.amount,
                "total_balance": total_balance,
                "transaction_id": transactionid,
                "timestamp": datetime.now().isoformat()
            })
            
            return MachineControlResponse(
                success=True,
                message=f"Cashout of ${cashout_amount:.2f} initiated successfully",
                execution_time_ms=execution_time,
                data=response_data
            )
            
        except Exception as cashout_error:
            # Broadcast failure event
            await broadcast_money_event("cashout_failed", {
                "success": False,
                "requested_amount": request.amount,
                "error": str(cashout_error),
                "timestamp": datetime.now().isoformat()
            })
            
            raise HTTPException(
                status_code=500,
                detail=f"AFT cashout failed: {str(cashout_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cashout error: {str(e)}"
        )


@router.get("/balance", response_model=MachineControlResponse)
async def get_balance(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Query current balance on the slot machine
    """
    try:
        start_time = datetime.now()
        
        # Check SAS communication availability
        if not (sas_service.slot_machine_app and 
                sas_service.slot_machine_app.sas_comm):
            raise HTTPException(
                status_code=503,
                detail="SAS communication not available"
            )
        
        sas_comm = sas_service.slot_machine_app.sas_comm
        
        # Query balance using SAS money functions
        try:
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                result = sas_comm.sas_money.komut_bakiye_sorgulama(
                    sender=1,  # Info query
                    isforinfo=1,  # Information only
                    sendertext="API-Balance-Query"
                )
                
                # Wait briefly for balance response
                await asyncio.sleep(0.5)
                
                # Get current balance
                current_balance = sas_comm.sas_money.yanit_bakiye_tutar
                restricted_balance = sas_comm.sas_money.yanit_restricted_amount
                nonrestricted_balance = sas_comm.sas_money.yanit_nonrestricted_amount
                
                total_balance = current_balance + restricted_balance + nonrestricted_balance
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Prepare response data
                balance_data = {
                    "cashable_balance": float(current_balance),
                    "restricted_balance": float(restricted_balance),
                    "nonrestricted_balance": float(nonrestricted_balance),
                    "total_balance": float(total_balance),
                    "currency": "USD"  # Assuming USD, could be configurable
                }
                
                # Broadcast WebSocket event for balance query
                await broadcast_money_event("balance_queried", {
                    "success": True,
                    "balance_data": balance_data,
                    "timestamp": datetime.now().isoformat()
                })
                
                return MachineControlResponse(
                    success=True,
                    message="Balance retrieved successfully",
                    execution_time_ms=execution_time,
                    data=balance_data
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="SAS money functions not available"
                )
                
        except Exception as balance_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query balance: {str(balance_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Balance query error: {str(e)}"
        )


@router.post("/cancel-transfer", response_model=MachineControlResponse)
async def cancel_aft_transfer(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Cancel any pending AFT transfer operation
    """
    try:
        start_time = datetime.now()
        
        # Check SAS communication availability
        if not (sas_service.slot_machine_app and 
                sas_service.slot_machine_app.sas_comm):
            raise HTTPException(
                status_code=503,
                detail="SAS communication not available"
            )
        
        sas_comm = sas_service.slot_machine_app.sas_comm
        
        # Cancel AFT transfer using SAS money functions
        try:
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                result = sas_comm.sas_money.komut_cancel_aft_transfer()
            else:
                # Fallback to direct method if available
                result = sas_comm.money_cancel_aft_transfer()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Broadcast WebSocket event for cancel transfer
            await broadcast_money_event("transfer_cancelled", {
                "success": True,
                "action": "cancel_transfer",
                "timestamp": datetime.now().isoformat()
            })
            
            return MachineControlResponse(
                success=True,
                message="AFT transfer cancellation initiated",
                execution_time_ms=execution_time,
                data={
                    "action": "cancel_transfer",
                    "command_sent": "AFT Cancel Command (0x72, 0x01, 0x80)"
                }
            )
            
        except Exception as cancel_error:
            raise HTTPException(
                status_code=500,
                detail=f"AFT transfer cancellation failed: {str(cancel_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cancel transfer error: {str(e)}"
        )


def get_transfer_type_name(transfer_type: str) -> str:
    """Get human-readable name for transfer type"""
    type_names = {
        "00": "Non-Restricted",
        "10": "Cashable", 
        "11": "Restricted"
    }
    return type_names.get(transfer_type, "Unknown") 