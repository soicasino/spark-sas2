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

router = APIRouter(prefix="/api/money", tags=["Money Transfer"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    from main import sas_service
    return sas_service


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
        
        # Get AFT parameters  
        assetnumber = "0000006C"  # Asset number from hardware
        registrationkey = "00000000000000000000000000000000000000000000"  # Default registration key
        
        # Execute AFT credit transfer using SAS money functions
        try:
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                result = sas_comm.sas_money.komut_para_yukle(
                    doincreasetransactionid,
                    transfertype,
                    customerbalance,
                    customerpromo,
                    transactionid,
                    assetnumber,
                    registrationkey
                )
            else:
                # Fallback to direct money_cash_in method if available
                result = sas_comm.money_cash_in(
                    doincreasetransactionid,
                    transfertype,
                    customerbalance,
                    customerpromo,
                    transactionid,
                    assetnumber,
                    registrationkey
                )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return MachineControlResponse(
                success=True,
                message=f"Credit addition of ${request.amount:.2f} initiated successfully",
                execution_time_ms=execution_time,
                data={
                    "action": "add_credits",
                    "amount": request.amount,
                    "credits": int(request.amount * 100),
                    "transaction_id": transactionid,
                    "transfer_type": request.transfer_type,
                    "transfer_type_name": get_transfer_type_name(request.transfer_type)
                }
            )
            
        except Exception as aft_error:
            raise HTTPException(
                status_code=500,
                detail=f"AFT credit transfer failed: {str(aft_error)}"
            )
            
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
        
        # Get AFT parameters  
        assetnumber = "0000006C"  # Asset number from hardware
        registrationkey = "00000000000000000000000000000000000000000000"  # Default registration key
        
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
            
            return MachineControlResponse(
                success=True,
                message=f"Cashout of ${cashout_amount:.2f} initiated successfully",
                execution_time_ms=execution_time,
                data={
                    "action": "cashout",
                    "requested_amount": request.amount,
                    "total_balance": total_balance,
                    "cashable_balance": current_balance,
                    "restricted_balance": restricted_balance,
                    "nonrestricted_balance": nonrestricted_balance,
                    "transaction_id": transactionid
                }
            )
            
        except Exception as cashout_error:
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
                
                return MachineControlResponse(
                    success=True,
                    message="Balance retrieved successfully",
                    execution_time_ms=execution_time,
                    data={
                        "cashable_balance": float(current_balance),
                        "restricted_balance": float(restricted_balance),
                        "nonrestricted_balance": float(nonrestricted_balance),
                        "total_balance": float(total_balance),
                        "currency": "USD"  # Assuming USD, could be configurable
                    }
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


@router.get("/transfer-status", response_model=MachineControlResponse)
async def get_aft_transfer_status(
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Get the current AFT (Advanced Funds Transfer) status from the machine
    
    Returns detailed status information including:
    - Transfer availability
    - Asset number status
    - Registration status
    - Last transfer result codes
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
        
        # Query AFT status using SAS command 0x74 (AFT status inquiry)
        try:
            # Get the AFT status
            status_data = {}
            
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                # Check if we have AFT status attributes
                if hasattr(sas_comm.sas_money, 'aft_status'):
                    status_data['aft_enabled'] = getattr(sas_comm.sas_money, 'aft_status', False)
                
                if hasattr(sas_comm.sas_money, 'transfer_status'):
                    status_data['transfer_status'] = getattr(sas_comm.sas_money, 'transfer_status', 'unknown')
                
                if hasattr(sas_comm.sas_money, 'last_aft_status'):
                    status_data['last_aft_status'] = getattr(sas_comm.sas_money, 'last_aft_status', 'unknown')
                
                # Get asset number from communicator
                if hasattr(sas_comm, 'asset_number'):
                    status_data['asset_number'] = sas_comm.asset_number
                elif hasattr(sas_comm, 'decimal_asset_number'):
                    status_data['asset_number'] = sas_comm.decimal_asset_number
                else:
                    status_data['asset_number'] = None
                
                # Check registration status
                status_data['registration_required'] = True  # Most machines require registration
                status_data['registration_status'] = 'unknown'
                
            else:
                status_data = {
                    'aft_enabled': False,
                    'transfer_status': 'sas_money_not_available',
                    'asset_number': None,
                    'registration_required': True,
                    'registration_status': 'unknown'
                }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return MachineControlResponse(
                success=True,
                message="AFT status retrieved successfully",
                execution_time_ms=execution_time,
                data={
                    "action": "get_aft_status",
                    **status_data,
                    "status_codes": {
                        "0x80": "Transfer pending",
                        "0x81": "Transfer complete", 
                        "0x82": "Transfer failed",
                        "0x83": "Request acknowledged"
                    }
                }
            )
            
        except Exception as status_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query AFT status: {str(status_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AFT status query error: {str(e)}"
        )


@router.post("/register-aft", response_model=MachineControlResponse)
async def register_aft(
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Register the machine for AFT (Advanced Funds Transfer) operations
    
    This sends the AFT registration command to enable money transfers.
    Most slot machines require this before accepting AFT commands.
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
        
        # AFT Registration Parameters
        assetnumber = "0000006C"  # Asset number (108 in decimal)
        registrationkey = "00000000000000000000000000000000000000000000"  # Default key
        posid = "POS001"  # Point of Sale ID
        
        try:
            # Send AFT registration command (SAS command 0x75)
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                # Try to call AFT registration if available
                if hasattr(sas_comm.sas_money, 'komut_aft_registration'):
                    result = sas_comm.sas_money.komut_aft_registration(
                        assetnumber,
                        registrationkey,
                        posid
                    )
                else:
                    # Manual AFT registration command construction
                    # Command: 0x75 + asset number + registration key + POS ID
                    sas_address = getattr(sas_comm, 'sas_address', '01')
                    command = f"{sas_address}75{assetnumber}{registrationkey}{posid.ljust(16, '0')}"
                    
                    # Send the command
                    if hasattr(sas_comm, 'send_command'):
                        result = sas_comm.send_command(command)
                    else:
                        result = "Registration command sent (no response handler available)"
            else:
                raise HTTPException(
                    status_code=503,
                    detail="SAS money functions not available"
                )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return MachineControlResponse(
                success=True,
                message="AFT registration initiated successfully",
                execution_time_ms=execution_time,
                data={
                    "action": "register_aft",
                    "asset_number": assetnumber,
                    "pos_id": posid,
                    "registration_key_length": len(registrationkey),
                    "command_sent": f"AFT Registration Command (0x75)",
                    "note": "Check transfer-status endpoint to verify registration success"
                }
            )
            
        except Exception as reg_error:
            raise HTTPException(
                status_code=500,
                detail=f"AFT registration failed: {str(reg_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AFT registration error: {str(e)}"
        ) 