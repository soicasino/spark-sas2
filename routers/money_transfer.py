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
        
        # SAS configuration parameters
        assetnumber = sas_comm.sas_address if hasattr(sas_comm, 'sas_address') else "01000000"
        registrationkey = "00000000000000000000000000000000000000000000"  # 20 bytes of zeros
        
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