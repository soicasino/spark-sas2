"""
Money Transfer Router - Handle AFT (Advanced Funds Transfer) operations
Based on para_commands.py.ref implementation for SAS protocol
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from decimal import Decimal
import asyncio
import time

from models.requests import MoneyTransferRequest, CashoutRequest
from models.responses import MachineControlResponse, ErrorResponse
from sas_web_service import SASWebService
from services.event_service import event_service
from websocket_manager import connection_manager

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
    
    - **transfer_type**: Type of transfer ("00" for cashable, "11" for restricted/jackpot, based on original working code)
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
        transfertype = int(request.transfer_type)  # 00=cashable, 11=restricted/jackpot (per original code)
        amount = float(request.amount)  # Amount in dollars
        customerpromo = 0.0  # No promotional amount for basic transfers
        
        # Generate transaction ID or use provided one
        if request.transaction_id:
            transactionid = int(request.transaction_id) if request.transaction_id.isdigit() else hash(request.transaction_id) % 10000
        else:
            transactionid = int(datetime.now().timestamp()) % 10000
        
        # Get AFT parameters  
        # Try to get asset number from machine, fallback to default
        if hasattr(sas_comm, 'asset_number') and sas_comm.asset_number:
            assetnumber = sas_comm.asset_number
        else:
            assetnumber = "0000006C"  # Asset number fallback (108 in decimal)
        
        # Execute AFT credit transfer using SAS money functions
        try:
            # Use all-zeros registration key (confirmed working with this machine)
            registrationkey = "0000000000000000000000000000000000000000"
            print(f"[ADD CREDITS] Using all-zeros registration key: {registrationkey}")
            
            # Register AFT before transfer
            print(f"[ADD CREDITS] Registering AFT before money transfer...")
            registration_result = sas_comm.sas_money.komut_aft_registration(
                assetnumber, registrationkey, "POS001"
            )
            print(f"[ADD CREDITS] AFT registration result: {registration_result}")
            
            # Use the DIRECT AFT approach that matches the original working code
            print(f"[ADD CREDITS] ===== ATTEMPTING DIRECT AFT TRANSFER (ORIGINAL WORKING APPROACH) =====")
            print(f"[ADD CREDITS] Skipping auto-lock workflow - using direct AFT like original working code")
            
            try:
                # DIRECT AFT TRANSFER - Exactly matches original raspberryPython_orj.py approach
                # NO AFT LOCK/UNLOCK - Original never used these commands
                print(f"[ADD CREDITS] Executing DIRECT AFT transfer (no lock/unlock, matches original)...")
                
                # Reset transfer status flags exactly like original Wait_ParaYukle
                sas_comm.sas_money.global_para_yukleme_transfer_status = "0"
                sas_comm.sas_money.is_waiting_for_para_yukle = 1
                
                # Send direct AFT transfer command
                transaction_id = sas_comm.sas_money.komut_para_yukle(
                    doincreasetransactionid=1,  # Increment transaction ID like original
                    transfertype=int(request.transfer_type),  # Use exact transfer type from request
                    customerbalance=amount,
                    customerpromo=0.0,
                    assetnumber=assetnumber,
                    registrationkey=registrationkey
                )
                
                if transaction_id is None:
                    raise Exception("Direct AFT transfer command failed")
                
                print(f"[ADD CREDITS] Direct AFT command sent, transaction ID: {transaction_id}")
                print(f"[ADD CREDITS] Using BLOCKING wait loop (exactly matches original Wait_ParaYukle)...")
                
                # Use BLOCKING wait exactly like original - no async
                wait_result = sas_comm.sas_money.wait_for_para_yukle_completion_blocking_original(timeout=30)
                
                if wait_result is True:
                    print(f"[ADD CREDITS] ✅ BLOCKING WAIT SUCCESS - Direct AFT transfer completed!")
                    
                    # Query updated balance
                    print(f"[ADD CREDITS] Querying updated balance...")
                    sas_comm.sas_money.komut_bakiye_sorgulama("add_credits_success", False, "post_transfer_balance")
                    await asyncio.sleep(2)  # Give time for balance response
                    
                    updated_cashable = getattr(sas_comm.sas_money, 'yanit_bakiye_tutar', 0.0)
                    updated_restricted = getattr(sas_comm.sas_money, 'yanit_restricted_amount', 0.0)
                    updated_nonrestricted = getattr(sas_comm.sas_money, 'yanit_nonrestricted_amount', 0.0)
                    total_balance = updated_cashable + updated_restricted + updated_nonrestricted
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    return MachineControlResponse(
                        success=True,
                        message=f"💰 Credit addition of ${request.amount:.2f} completed successfully using direct AFT (original approach)",
                        execution_time_ms=execution_time,
                        data={
                            "action": "add_credits",
                            "amount": request.amount,
                            "credits": int(request.amount * 100),
                            "transaction_id": transaction_id,
                            "transfer_type": request.transfer_type,
                            "transfer_type_name": get_transfer_type_name(request.transfer_type),
                            "status": "completed_direct_aft",
                            "method": "direct_aft_original_approach",
                            "updated_balance": {
                                "cashable": float(updated_cashable),
                                "restricted": float(updated_restricted),
                                "nonrestricted": float(updated_nonrestricted),
                                "total": float(total_balance)
                            }
                        }
                    )
                    
                elif wait_result is False:
                    # Transfer failed with error status
                    final_status = getattr(sas_comm.sas_money, 'global_para_yukleme_transfer_status', 'Unknown')
                    error_msg = f"Direct AFT transfer failed with status: {final_status}"
                    print(f"[ADD CREDITS] ❌ DIRECT AFT FAILED: {error_msg}")
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    return MachineControlResponse(
                        success=False,
                        message=f"❌ Credit addition failed: {error_msg}",
                        execution_time_ms=execution_time,
                        data={
                            "action": "add_credits",
                            "amount": request.amount,
                            "transaction_id": transaction_id,
                            "error": error_msg,
                            "final_status": final_status,
                            "method": "direct_aft_original_approach"
                        }
                    )
                    
                else:
                    # Timeout
                    print(f"[ADD CREDITS] ⏱️ DIRECT AFT TIMEOUT")
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    return MachineControlResponse(
                        success=False,
                        message="⏱️ Credit addition timed out - no response from machine",
                        execution_time_ms=execution_time,
                        data={
                            "action": "add_credits",
                            "amount": request.amount,
                            "transaction_id": transaction_id,
                            "error": "timeout",
                            "method": "direct_aft_original_approach"
                        }
                    )
            
            except Exception as direct_error:
                print(f"[ADD CREDITS] ❌ Direct AFT also failed: {direct_error}")
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                return MachineControlResponse(
                    success=False,
                    message=f"❌ Direct AFT transfer failed: {direct_error}",
                    execution_time_ms=execution_time,
                    data={
                        "action": "add_credits",
                        "amount": request.amount,
                        "error": str(direct_error),
                        "method": "direct_aft_original_approach"
                    }
                )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Money transfer error: {str(e)}"
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
        
        # First query current credits to check available funds
        try:
            # Query current credits using meter system instead of balance query
            # since the machine doesn't respond to SAS 74h balance queries
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                print("[CASHOUT] Querying current credits via meter system...")
                
                # Get current meters to check credits
                sas_comm.sas_money.get_meter(isall=0)
                
                # Wait a moment for meter response
                await asyncio.sleep(1)
                
                # Get current credits from parsed meters
                current_credits = 0
                if hasattr(sas_comm.sas_money, 'last_parsed_meters') and sas_comm.sas_money.last_parsed_meters:
                    meters = sas_comm.sas_money.last_parsed_meters
                    # Look for current credits in various possible meter names
                    current_credits = (
                        meters.get('current_credits', 0) or
                        meters.get('total_coin_in', 0) - meters.get('total_coin_out', 0) or
                        0
                    )
                    print(f"[CASHOUT] Current credits from meters: {current_credits}")
                else:
                    print("[CASHOUT] No meter data available")
                
                # Convert to dollars if needed (assuming credits are in cents)
                if current_credits > 1000:  # Likely in cents
                    current_balance = current_credits / 100
                else:
                    current_balance = current_credits
                
                print(f"[CASHOUT] Available balance: ${current_balance:.2f}")
                
                if current_balance <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="No balance available to cashout"
                    )
                
                # Check if requested amount is available
                if request.amount and request.amount > current_balance:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Requested amount ${request.amount:.2f} exceeds available balance ${current_balance:.2f}"
                    )
            
            else:
                raise HTTPException(
                    status_code=503,
                    detail="SAS money functions not available"
                )
            
        except HTTPException:
            raise
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
        # Try to get asset number from machine, fallback to default
        if hasattr(sas_comm, 'asset_number') and sas_comm.asset_number:
            assetnumber = sas_comm.asset_number
        else:
            assetnumber = "0000006C"  # Asset number fallback (108 in decimal)
        
        # Execute AFT cashout using SAS money functions
        try:
            # Use all-zeros registration key (standard for AFT)
            # TODO: get from config later 
            registrationkey = "0000000000000000000000000000000000000000"
            
            # Send the cashout command
            actual_transaction_id = sas_comm.sas_money.komut_para_sifirla(
                doincreaseid,
                transactionid,
                assetnumber,
                registrationkey
            )
            
            # Wait for completion with timeout
            wait_result = await sas_comm.sas_money.wait_for_para_sifirla_completion(timeout=15)
            
            cashout_amount = request.amount if request.amount else current_balance
            
            if wait_result is True:
                # Success - cashout completed
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                return MachineControlResponse(
                    success=True,
                    message=f"Cashout of ${cashout_amount:.2f} completed successfully",
                    execution_time_ms=execution_time,
                    data={
                        "action": "cashout",
                        "requested_amount": request.amount,
                        "total_balance": current_balance,
                        "cashable_balance": current_balance,
                        "restricted_balance": 0,
                        "nonrestricted_balance": 0,
                        "transaction_id": actual_transaction_id,
                        "status": "completed"
                    }
                )
            elif wait_result is False:
                # Cashout failed
                status_code = sas_comm.sas_money.global_para_silme_transfer_status
                status_desc = sas_comm.sas_money.get_transfer_status_description(status_code)
                raise HTTPException(
                    status_code=400,
                    detail=f"AFT cashout failed: {status_desc} (Code: {status_code})"
                )
            else:
                # Timeout
                raise HTTPException(
                    status_code=504,
                    detail="AFT cashout timed out - machine did not respond within 15 seconds"
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
    Query current AFT balance on the slot machine
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
        
        # Query AFT balance using SAS command 74h (AFT status request)
        try:
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                print("[BALANCE] Querying AFT balance via balance query...")
                
                # Send AFT balance query (SAS command 74h)
                sas_comm.sas_money.komut_bakiye_sorgulama("balance_api", False, "api_balance_query")
                
                # Wait for balance response
                balance_result = await sas_comm.sas_money.wait_for_bakiye_sorgulama_completion(timeout=5)
                
                if balance_result:
                    # Get the parsed balance amounts
                    cashable_balance = getattr(sas_comm.sas_money, 'yanit_bakiye_tutar', 0)
                    restricted_balance = getattr(sas_comm.sas_money, 'yanit_restricted_amount', 0)
                    nonrestricted_balance = getattr(sas_comm.sas_money, 'yanit_nonrestricted_amount', 0)
                    
                    print(f"[BALANCE] AFT Balance retrieved:")
                    print(f"[BALANCE]   Cashable: {cashable_balance}")
                    print(f"[BALANCE]   Restricted: {restricted_balance}")
                    print(f"[BALANCE]   Non-restricted: {nonrestricted_balance}")
                    
                    total_balance = cashable_balance + restricted_balance + nonrestricted_balance
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    return MachineControlResponse(
                        success=True,
                        message="AFT balance retrieved successfully",
                        execution_time_ms=execution_time,
                        data={
                            "cashable_balance": float(cashable_balance),
                            "restricted_balance": float(restricted_balance),
                            "nonrestricted_balance": float(nonrestricted_balance),
                            "total_balance": float(total_balance),
                            "currency": "USD"
                        }
                    )
                else:
                    print("[BALANCE] AFT balance query timed out")
                    # Fallback to current stored values
                    cashable_balance = getattr(sas_comm.sas_money, 'yanit_bakiye_tutar', 0)
                    restricted_balance = getattr(sas_comm.sas_money, 'yanit_restricted_amount', 0)
                    nonrestricted_balance = getattr(sas_comm.sas_money, 'yanit_nonrestricted_amount', 0)
                    total_balance = cashable_balance + restricted_balance + nonrestricted_balance
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    return MachineControlResponse(
                        success=True,
                        message="AFT balance retrieved from cache (query timeout)",
                        execution_time_ms=execution_time,
                        data={
                            "cashable_balance": float(cashable_balance),
                            "restricted_balance": float(restricted_balance),
                            "nonrestricted_balance": float(nonrestricted_balance),
                            "total_balance": float(total_balance),
                            "currency": "USD"
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
                detail=f"Failed to query AFT balance: {str(balance_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AFT balance query error: {str(e)}"
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
        "00": "Cashable",     # Fixed: 00 is cashable per original code
        "10": "Jackpot",      # 10 is for jackpots in original
        "11": "Restricted"    # 11 is restricted jackpot
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
        
        # Step 1: Read asset number from machine first
        print(f"[AFT REGISTRATION] Step 1: Reading asset number from machine...")
        try:
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                if hasattr(sas_comm.sas_money, 'komut_read_asset_number'):
                    asset_result = sas_comm.sas_money.komut_read_asset_number()
                    print(f"[AFT REGISTRATION] Asset number query result: {asset_result}")
                    
                    # Wait for response
                    await asyncio.sleep(1)
                    
                    # Try to get asset number from communicator
                    if hasattr(sas_comm, 'asset_number') and sas_comm.asset_number:
                        assetnumber = sas_comm.asset_number
                        print(f"[AFT REGISTRATION] Using machine asset number: {assetnumber}")
                    else:
                        assetnumber = "0000006C"  # Fallback
                        print(f"[AFT REGISTRATION] Using fallback asset number: {assetnumber}")
                else:
                    assetnumber = "0000006C"  # Fallback
                    print(f"[AFT REGISTRATION] Using default asset number: {assetnumber}")
            else:
                assetnumber = "0000006C"  # Fallback
                print(f"[AFT REGISTRATION] Using default asset number: {assetnumber}")
        except Exception as asset_error:
            print(f"[AFT REGISTRATION] Error reading asset number: {asset_error}")
            assetnumber = "0000006C"  # Fallback
        
        # AFT Registration Parameters
        registrationkey = "00000000000000000000000000000000000000000000"  # Default key
        posid = "POS001"  # Point of Sale ID
        
        try:
            # Step 2: Send AFT registration command
            print(f"[AFT REGISTRATION] Step 2: Performing AFT registration...")
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                # Try to call AFT registration if available
                if hasattr(sas_comm.sas_money, 'komut_aft_registration'):
                    result = sas_comm.sas_money.komut_aft_registration(
                        assetnumber,
                        registrationkey,
                        posid
                    )
                    print(f"[AFT REGISTRATION] Registration result: {result}")
                else:
                    # Manual AFT registration command construction
                    # Command: 0x75 + asset number + registration key + POS ID
                    sas_address = getattr(sas_comm, 'sas_address', '01')
                    command = f"{sas_address}75{assetnumber}{registrationkey}{posid.ljust(16, '0')}"
                    
                    # Send the command
                    if hasattr(sas_comm, 'send_command'):
                        result = sas_comm.send_command(command)
                        print(f"[AFT REGISTRATION] Manual registration command sent: {result}")
                    else:
                        result = "Registration command sent (no response handler available)"
                        print(f"[AFT REGISTRATION] {result}")
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


@router.get("/aft-debug", response_model=MachineControlResponse)
async def aft_debug_status(
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Comprehensive AFT debugging information to help diagnose transfer issues.
    
    Shows:
    - Current AFT status and lock state
    - Asset number information  
    - Transfer status codes from the machine
    - SAS money system status
    - Last transfer results
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
        debug_info = {}
        
        # 1. Asset Number Information
        debug_info['asset_number'] = {
            'hex_format': getattr(sas_comm, 'asset_number', None),
            'decimal_format': getattr(sas_comm, 'decimal_asset_number', None),
            'for_aft': sas_comm.get_asset_number_for_aft() if hasattr(sas_comm, 'get_asset_number_for_aft') else None
        }
        
        # 2. SAS Money System Status
        if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
            sas_money = sas_comm.sas_money
            debug_info['sas_money_status'] = {
                'available': True,
                'last_balance_query': {
                    'cashable': float(getattr(sas_money, 'yanit_bakiye_tutar', 0)),
                    'restricted': float(getattr(sas_money, 'yanit_restricted_amount', 0)),
                    'nonrestricted': float(getattr(sas_money, 'yanit_nonrestricted_amount', 0))
                },
                'transfer_status': {
                    'para_yukleme_status': getattr(sas_money, 'global_para_yukleme_transfer_status', None),
                    'para_silme_status': getattr(sas_money, 'global_para_silme_transfer_status', None),
                    'waiting_for_para_yukle': getattr(sas_money, 'is_waiting_for_para_yukle', 0),
                    'waiting_for_bakiye_sifirla': getattr(sas_money, 'is_waiting_for_bakiye_sifirla', 0)
                },
                'transaction_info': {
                    'yukle_first_transaction': getattr(sas_money, 'yukle_first_transaction', 0),
                    'yukle_last_transaction': getattr(sas_money, 'yukle_last_transaction', 0),
                    'sifirla_first_transaction': getattr(sas_money, 'sifirla_first_transaction', 0),
                    'sifirla_last_transaction': getattr(sas_money, 'sifirla_last_transaction', 0)
                }
            }
        else:
            debug_info['sas_money_status'] = {
                'available': False,
                'reason': 'SAS money system not initialized'
            }
        
        # 3. AFT Protocol Status Interpretation
        debug_info['aft_protocol_status'] = {
            'status_code_meanings': {
                '00': 'Transfer successful',
                '01': 'Transfer pending', 
                '40': 'Transfer amount exceeds limit',
                '41': 'Amount not even multiple of denomination',
                '42': 'Amount not even multiple of accounting denomination',
                '43': 'Amount exceeds machine transfer limit',
                '80': 'Machine not registered for AFT',
                '81': 'Registration key mismatch',
                '82': 'No POS ID',
                '83': 'No won amount available for cashout'
            },
            'current_status': getattr(sas_comm.sas_money, 'global_para_yukleme_transfer_status', 'unknown') if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money else 'unknown'
        }
        
        # 4. Machine Communication Status
        debug_info['communication_status'] = {
            'port_open': getattr(sas_comm, 'is_port_open', False),
            'port_name': getattr(sas_comm, 'port_name', None),
            'sas_address': getattr(sas_comm, 'sas_address', None),
            'device_type': getattr(sas_comm, 'device_type_id', None),
            'last_communication': 'Recently active' if hasattr(sas_comm, 'last_80_time') else 'Unknown'
        }
        
        # 5. AFT Recommendations
        recommendations = []
        
        # Check asset number
        if not debug_info['asset_number']['hex_format']:
            recommendations.append("Asset number not read from machine - try restarting SAS communication")
        
        # Check AFT status
        current_status = debug_info['aft_protocol_status']['current_status']
        if current_status == '80':
            recommendations.append("Machine not registered for AFT - run /register-aft endpoint")
        elif current_status == '81':
            recommendations.append("AFT registration key mismatch - check asset number format")
        elif current_status == '82':
            recommendations.append("No POS ID configured - check AFT registration")
        elif current_status == 'unknown':
            recommendations.append("No AFT status received - machine may not support AFT or need registration")
        
        # Check if transfers are being attempted
        if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
            if getattr(sas_comm.sas_money, 'is_waiting_for_para_yukle', 0):
                recommendations.append("Transfer in progress - wait for completion before trying another")
        
        debug_info['recommendations'] = recommendations
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return MachineControlResponse(
            success=True,
            message="AFT debug information retrieved successfully",
            execution_time_ms=execution_time,
            data={
                "action": "aft_debug",
                **debug_info,
                "next_steps": [
                    "1. Check AFT registration status",
                    "2. Verify asset number is properly read",
                    "3. Send AFT lock/status request (0x74)",
                    "4. Monitor transfer status codes",
                    "5. Check machine AFT capability"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AFT debug error: {str(e)}"
        )


@router.post("/force-unlock-aft", status_code=200)
async def force_unlock_aft(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Attempt an aggressive, multi-step unlock to clear hard locks (like FF)
    that prevent AFT transfers from being credited. Use with caution.
    """
    try:
        if not sas_service:
            raise HTTPException(status_code=503, detail="SAS service not available")

        result = await sas_service.execute_command_async("machine_force_unlock", {})
        
        return {
            "success": True,
            "message": "Aggressive AFT unlock sequence executed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Force unlock AFT error: {str(e)}") 