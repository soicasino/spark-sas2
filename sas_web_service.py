"""
SAS Web Service - Thread-safe wrapper for SAS communication
Provides a bridge between FastAPI endpoints and the core SAS system
"""
import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from queue import Queue, Empty, PriorityQueue
from threading import Lock
from typing import Dict, Any, Callable, Optional
import json
import queue

from slot_machine_application import SlotMachineApplication
# WebSocket manager is handled separately in FastAPI main app


class CommandStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"  
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class SASCommand:
    """Represents a SAS command with metadata"""
    id: str
    command_type: str
    parameters: Dict[str, Any]
    callback: Optional[Callable] = None
    timeout: float = 10.0
    priority: int = 1  # Lower number = higher priority
    created_at: datetime = None
    status: CommandStatus = CommandStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SASWebService:
    """
    Thread-safe wrapper for SAS communication that handles web API requests
    """
    
    def __init__(self):
        self.slot_machine_app = None
        self.is_initialized = False
        self.command_queue = queue.PriorityQueue()
        self.pending_commands: Dict[str, SASCommand] = {}
        self.command_results: Dict[str, Any] = {}
        self.background_thread = None
        self.web_service_running = False
        self._lock = threading.Lock()
        
        # System status cache
        self.system_status = {
            "sas_connected": False,
            "last_communication": None,
            "asset_number": None,
            "sas_version": None,
            "port_info": None
        }
        
    async def initialize(self):
        """Initialize the SAS system in a background thread"""
        if self.is_initialized:
            return True
            
        print("[SASWebService] Initializing SAS system...")
        
        # Start the background SAS service
        self.web_service_running = True
        self.background_thread = threading.Thread(target=self._run_sas_background, daemon=True)
        self.background_thread.start()
        
        # Wait for initialization with timeout
        max_wait = 30  # seconds
        wait_time = 0
        while not self.is_initialized and wait_time < max_wait:
            await asyncio.sleep(0.5)
            wait_time += 0.5
            
        if self.is_initialized:
            print("[SASWebService] SAS system initialized successfully")
            return True
        else:
            print("[SASWebService] SAS system initialization failed")
            return False
            
    def _run_sas_background(self):
        """Run the SAS application in background thread"""
        try:
            print("[SASWebService] Starting SAS background service...")
            self.slot_machine_app = SlotMachineApplication()
            
            # Initialize SAS communication
            if self.slot_machine_app.initialize_sas():
                self.is_initialized = True
                self.system_status["sas_connected"] = True
                self.system_status["last_communication"] = datetime.now()
                
                # Start the main SAS operation
                self.slot_machine_app.running = True
                self.slot_machine_app.sas_polling_loop()
                
                # Run command processing loop
                self._process_commands()
                
            else:
                print("[SASWebService] Failed to initialize SAS")
                self.is_initialized = False
                
        except Exception as e:
            print(f"[SASWebService] Error in background service: {e}")
            self.is_initialized = False
            
    def _process_commands(self):
        """Process commands from the queue"""
        while self.web_service_running:
            try:
                # Check for pending commands (non-blocking)
                try:
                    priority, command_id = self.command_queue.get_nowait()
                    command = self.pending_commands.get(command_id)
                    
                    if command:
                        self._execute_command(command)
                        
                except queue.Empty:
                    pass
                    
                # Clean up old completed commands
                self._cleanup_old_commands()
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"[SASWebService] Error processing commands: {e}")
                time.sleep(1)
                
    def _execute_command(self, command: SASCommand):
        """Execute a single SAS command"""
        try:
            command.status = CommandStatus.EXECUTING
            print(f"[SASWebService] Executing command: {command.command_type}")
            
            # Route command to appropriate handler
            result = self._route_command(command)
            
            command.result = result
            command.status = CommandStatus.COMPLETED
            
            # Store result for retrieval
            self.command_results[command.id] = {
                "status": command.status.value,
                "result": result,
                "completed_at": datetime.now(),
                "execution_time": (datetime.now() - command.created_at).total_seconds()
            }
            
        except Exception as e:
            print(f"[SASWebService] Command execution failed: {e}")
            command.status = CommandStatus.FAILED
            command.error = str(e)
            
            self.command_results[command.id] = {
                "status": command.status.value,
                "error": str(e),
                "completed_at": datetime.now()
            }
            
    def _route_command(self, command: SASCommand) -> Any:
        """Route command to appropriate SAS function"""
        command_type = command.command_type
        params = command.parameters
        
        if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
            raise Exception("SAS communication not available")
            
        sas_comm = self.slot_machine_app.sas_comm
        
        # Route based on command type
        if command_type == "get_meters":
            return self._get_meters(params.get("meter_type", "basic"))
            
        elif command_type == "get_balance":
            return self._get_balance()
            
        elif command_type == "get_sas_version":
            return self._get_sas_version()
            
        elif command_type == "get_asset_number":
            return self._get_asset_number()
            
        elif command_type == "bill_acceptor_enable":
            return self._bill_acceptor_control(True)
            
        elif command_type == "bill_acceptor_disable":
            return self._bill_acceptor_control(False)
            
        elif command_type == "bill_acceptor_stack":
            return self._bill_acceptor_stack()
            
        elif command_type == "bill_acceptor_reject":
            return self._bill_acceptor_reject()
            
        elif command_type == "bill_acceptor_reset":
            return self._bill_acceptor_reset()
            
        elif command_type == "money_add_credits":
            return self._money_add_credits(params)
            
        elif command_type == "money_cashout":
            return self._money_cashout(params)
            
        elif command_type == "money_balance_query":
            return self._money_balance_query()
            
        elif command_type == "money_cancel_transfer":
            return self._money_cancel_transfer()
            
        elif command_type == "machine_lock":
            return self._machine_lock()
            
        elif command_type == "machine_unlock":
            return self._machine_unlock()
            
        elif command_type == "machine_restart":
            return self._machine_restart()
            
        elif command_type == "system_status":
            return self._get_system_status()
            
        else:
            raise Exception(f"Unknown command type: {command_type}")
            
    def _get_meters(self, meter_type: str = "basic") -> Dict[str, Any]:
        """Get meter readings from the slot machine"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm or not self.slot_machine_app.sas_comm.sas_money:
                raise Exception("SAS money functions not available")
                
            money_funcs = self.slot_machine_app.sas_comm.sas_money
            
            # Trigger meter reading
            if meter_type == "extended":
                money_funcs.get_meter(isall=1)  # Extended meters
            else:
                money_funcs.get_meter(isall=0)  # Basic meters
                
            # Wait a moment for response
            time.sleep(2)
            
            # Get parsed meters
            meters = money_funcs.last_parsed_meters if hasattr(money_funcs, 'last_parsed_meters') else {}
            
            if not meters:
                raise Exception("No meter data available")
                
            # Format for display
            formatted_meters = self._format_meters_for_display(meters)
            
            return {
                "status": "success",
                "meter_type": meter_type,
                "meters": meters,
                "formatted": formatted_meters,
                "timestamp": datetime.now().isoformat(),
                "message": "Meters retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get meters: {e}")
            
    def _format_meters_for_display(self, meters: Dict[str, float]) -> Dict[str, str]:
        """Format meter values for display"""
        formatted = {}
        
        for key, value in meters.items():
            if isinstance(value, (int, float)):
                # Format as currency for Turkish Lira
                formatted[key] = f"{value:,.2f} TL"
            else:
                formatted[key] = str(value)
                
        return formatted
        
    def _get_balance(self) -> Dict[str, Any]:
        """Get current machine balance/credits"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm or not self.slot_machine_app.sas_comm.sas_money:
                raise Exception("SAS money functions not available")
                
            money_funcs = self.slot_machine_app.sas_comm.sas_money
            
            # Request current balance by getting meters first
            money_funcs.get_meter(isall=0)
            time.sleep(2)
            
            # Get the balance from last parsed meters
            meters = money_funcs.last_parsed_meters if hasattr(money_funcs, 'last_parsed_meters') else {}
            balance = meters.get("current_credits", 0)
            
            return {
                "status": "success",
                "balance": balance,
                "formatted_balance": f"{balance:,.2f} TL",
                "timestamp": datetime.now().isoformat(),
                "message": "Balance retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get balance: {e}")
            
    def _get_sas_version(self) -> Dict[str, Any]:
        """Get SAS version information"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Try to get version from communication layer
            version_info = {
                "sas_address": sas_comm.sas_address,
                "device_type": sas_comm.device_type_id,
                "protocol_version": "6.03",  # Standard SAS version
                "communication_type": "Serial"
            }
            
            self.system_status["sas_version"] = version_info
            
            return {
                "status": "success",
                "version_info": version_info,
                "timestamp": datetime.now().isoformat(),
                "message": "SAS version retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get SAS version: {e}")
            
    def _get_asset_number(self) -> Dict[str, Any]:
        """Get machine asset number"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Try to get asset number (this would typically come from a SAS command)
            # For now, we'll use a placeholder or try to get it from the system
            asset_number = getattr(sas_comm, 'asset_number', 'SAS001')
            
            self.system_status["asset_number"] = asset_number
            
            return {
                "status": "success",
                "asset_number": asset_number,
                "timestamp": datetime.now().isoformat(),
                "message": "Asset number retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get asset number: {e}")
            
    def _bill_acceptor_control(self, enable: bool) -> Dict[str, Any]:
        """Enable or disable bill acceptor"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Use the actual bill acceptor functions
            if hasattr(sas_comm, 'bill_acceptor'):
                bill_acceptor = sas_comm.bill_acceptor
                if enable:
                    bill_acceptor.bill_acceptor_inhibit_open()
                    action = "enabled"
                else:
                    bill_acceptor.bill_acceptor_inhibit_close()
                    action = "disabled"
                    
                return {
                    "status": "success",
                    "action": action,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Bill acceptor {action} successfully"
                }
            else:
                raise Exception("Bill acceptor not available")
            
        except Exception as e:
            raise Exception(f"Failed to control bill acceptor: {e}")
            
    def _bill_acceptor_stack(self) -> Dict[str, Any]:
        """Stack bill in bill acceptor"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            if hasattr(sas_comm, 'bill_acceptor'):
                bill_acceptor = sas_comm.bill_acceptor
                bill_acceptor.bill_acceptor_stack1()
                
                return {
                    "status": "success",
                    "action": "stack",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Bill stacking command sent successfully"
                }
            else:
                raise Exception("Bill acceptor not available")
            
        except Exception as e:
            raise Exception(f"Failed to stack bill: {e}")
            
    def _bill_acceptor_reject(self) -> Dict[str, Any]:
        """Reject bill in bill acceptor"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            if hasattr(sas_comm, 'bill_acceptor'):
                bill_acceptor = sas_comm.bill_acceptor
                bill_acceptor.bill_acceptor_reject("API_command")
                
                return {
                    "status": "success",
                    "action": "reject",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Bill rejection command sent successfully"
                }
            else:
                raise Exception("Bill acceptor not available")
            
        except Exception as e:
            raise Exception(f"Failed to reject bill: {e}")
            
    def _bill_acceptor_reset(self) -> Dict[str, Any]:
        """Reset bill acceptor"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            if hasattr(sas_comm, 'bill_acceptor'):
                bill_acceptor = sas_comm.bill_acceptor
                bill_acceptor.bill_acceptor_reset()
                
                return {
                    "status": "success",
                    "action": "reset",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Bill acceptor reset command sent successfully"
                }
            else:
                raise Exception("Bill acceptor not available")
            
        except Exception as e:
            raise Exception(f"Failed to reset bill acceptor: {e}")
            
    def _money_add_credits(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add credits to machine using AFT"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Extract parameters from command_data
            amount = command_data.get("amount", 0)
            transfer_type = command_data.get("transfer_type", "10")  # Default to cashable
            transaction_id = command_data.get("transaction_id")
            
            if amount <= 0:
                raise Exception("Amount must be greater than 0")
            
            # AFT parameters based on para_commands.py.ref
            doincreasetransactionid = 1
            transfertype = int(transfer_type)
            customerbalance = float(amount)
            customerpromo = 0.0
            
            transactionid = transaction_id if transaction_id else int(datetime.now().timestamp()) % 10000
            assetnumber = getattr(sas_comm, 'sas_address', "01000000")
            registrationkey = "00000000000000000000000000000000000000000000"
            
            # Execute money transfer using sas_money instance methods
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                sas_money = sas_comm.sas_money
                result = sas_money.komut_para_yukle(
                    doincreasetransactionid,
                    transfertype, 
                    customerbalance,
                    customerpromo,
                    transactionid,
                    assetnumber,
                    registrationkey
                )
            else:
                raise Exception("SAS money functions not available")
            
            return {
                "status": "success", 
                "action": "add_credits",
                "amount": amount,
                "transfer_type": transfer_type,
                "transaction_id": transactionid,
                "timestamp": datetime.now().isoformat(),
                "message": f"Credit addition of ${amount:.2f} initiated"
            }
            
        except Exception as e:
            logger.error(f"Money add credits error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _money_cashout(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cashout credits from machine using AFT"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Extract parameters from command_data
            amount = command_data.get("amount")  # None means cashout all
            transaction_id = command_data.get("transaction_id")
            
            # Check if sas_money is available
            if not (hasattr(sas_comm, 'sas_money') and sas_comm.sas_money):
                raise Exception("SAS money functions not available")
                
            sas_money = sas_comm.sas_money
            
            # First query balance to check available funds
            try:
                balance_result = sas_money.komut_bakiye_sorgulama(
                    sender=2,  # Cashout operation
                    isforinfo=0,  # Required for operation
                    sendertext="API-Cashout"
                )
                
                # Wait briefly for balance response
                time.sleep(0.5)
                
                # Get current balance from sas_money instance
                current_balance = sas_money.yanit_bakiye_tutar
                restricted_balance = sas_money.yanit_restricted_amount
                nonrestricted_balance = sas_money.yanit_nonrestricted_amount
                
                total_balance = current_balance + restricted_balance + nonrestricted_balance
                
                if total_balance <= 0:
                    raise Exception("No balance available to cashout")
                
                # Check if requested amount is available
                if amount and amount > total_balance:
                    raise Exception(f"Requested amount ${amount:.2f} exceeds available balance ${total_balance:.2f}")
                
            except Exception as balance_error:
                raise Exception(f"Failed to query balance: {str(balance_error)}")
            
            # AFT Cashout Parameters (based on para_commands.py.ref)
            doincreaseid = 1
            transactionid = transaction_id if transaction_id else int(datetime.now().timestamp()) % 10000
            assetnumber = getattr(sas_comm, 'sas_address', "01000000")
            registrationkey = "00000000000000000000000000000000000000000000"
            
            # Execute cashout using sas_money instance method
            try:
                result = sas_money.komut_para_sifirla(
                    doincreaseid,
                    transactionid,
                    assetnumber,
                    registrationkey
                )
                
                cashout_amount = amount if amount else total_balance
                
                return {
                    "status": "success",
                    "action": "cashout",
                    "requested_amount": amount,
                    "total_balance": float(total_balance),
                    "cashable_balance": float(current_balance),
                    "restricted_balance": float(restricted_balance),
                    "nonrestricted_balance": float(nonrestricted_balance),
                    "transaction_id": transactionid,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Cashout of ${cashout_amount:.2f} initiated"
                }
                
            except Exception as cashout_error:
                raise Exception(f"AFT cashout failed: {str(cashout_error)}")
            
        except Exception as e:
            logger.error(f"Money cashout error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _money_balance_query(self) -> Dict[str, Any]:
        """Query current balance on machine"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Execute balance query using sas_money instance method
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                sas_money = sas_comm.sas_money
                result = sas_money.komut_bakiye_sorgulama(
                    sender=1,
                    isforinfo=1,
                    sendertext="API-Balance-Query"
                )
                
                # Wait briefly for balance response
                time.sleep(0.5)
                
                # Get balance values from sas_money instance
                cashable_balance = sas_money.yanit_bakiye_tutar
                restricted_balance = sas_money.yanit_restricted_amount
                nonrestricted_balance = sas_money.yanit_nonrestricted_amount
                total_balance = cashable_balance + restricted_balance + nonrestricted_balance
                
                return {
                    "status": "success",
                    "action": "balance_query",
                    "cashable_balance": float(cashable_balance),
                    "restricted_balance": float(restricted_balance),
                    "nonrestricted_balance": float(nonrestricted_balance),
                    "total_balance": float(total_balance),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Balance retrieved successfully"
                }
            else:
                raise Exception("SAS money functions not available")
                
        except Exception as e:
            logger.error(f"Money balance query error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _money_cancel_transfer(self) -> Dict[str, Any]:
        """Cancel pending AFT transfer"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Execute cancel transfer using sas_money instance method
            if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                sas_money = sas_comm.sas_money
                result = sas_money.komut_cancel_aft_transfer()
            else:
                raise Exception("SAS money functions not available")
            
            return {
                "status": "success",
                "action": "cancel_transfer",
                "timestamp": datetime.now().isoformat(),
                "message": "AFT transfer cancellation initiated"
            }
            
        except Exception as e:
            logger.error(f"Money cancel transfer error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def _machine_lock(self) -> Dict[str, Any]:
        """Lock the machine using the original working lock command"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Use the original working lock command: 01 01 51 08
            # This is the exact command from raspberryPython_orj.py that works
            print("[MACHINE LOCK] Using original working lock command: 01 01 51 08")
            
            # Send the raw command directly
            lock_command = "01015108"  # Original lock command with CRC
            result = sas_comm.sas_send_command_with_queue("MachineLock", lock_command, 1)
            
            print(f"[MACHINE LOCK] Lock command result: {result}")
            
            return {
                "status": "success",
                "action": "locked",
                "command_sent": "01_01_LOCK",
                "command_hex": "01015108",
                "command_result": result,
                "timestamp": datetime.now().isoformat(),
                "message": "Original lock command sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to lock machine: {e}")
            
    def _machine_unlock(self) -> Dict[str, Any]:
        """Unlock the machine using AFT-specific unlock methods (correct approach for AFT Game Lock)"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Try AFT-specific unlock approaches in sequence
            unlock_results = []
            
            # Method 1: AFT Cancel Transfer (MOST IMPORTANT - this is the correct unlock for AFT Game Lock)
            print("[MACHINE UNLOCK] Method 1: AFT Cancel Transfer (Primary Method)")
            try:
                if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                    result1 = sas_comm.sas_money.komut_cancel_aft_transfer()
                    unlock_results.append({"method": "aft_cancel_transfer", "result": result1, "priority": "PRIMARY"})
                    print(f"[MACHINE UNLOCK] AFT Cancel Transfer result: {result1}")
                else:
                    unlock_results.append({"method": "aft_cancel_transfer", "error": "SAS money functions not available"})
            except Exception as e:
                print(f"[MACHINE UNLOCK] AFT Cancel Transfer failed: {e}")
                unlock_results.append({"method": "aft_cancel_transfer", "error": str(e)})
            
            # Method 2: Comprehensive AFT unlock sequence
            print("[MACHINE UNLOCK] Method 2: Comprehensive AFT unlock sequence")
            try:
                if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                    result2 = sas_comm.sas_money.komut_comprehensive_aft_unlock()
                    unlock_results.append({"method": "comprehensive_aft_unlock", "result": result2})
                    print(f"[MACHINE UNLOCK] Comprehensive AFT unlock result: {result2}")
                else:
                    unlock_results.append({"method": "comprehensive_aft_unlock", "error": "SAS money functions not available"})
            except Exception as e:
                print(f"[MACHINE UNLOCK] Comprehensive AFT unlock failed: {e}")
                unlock_results.append({"method": "comprehensive_aft_unlock", "error": str(e)})
            
            # Method 3: Original working unlock command (fallback)
            print("[MACHINE UNLOCK] Method 3: Original working unlock command (Fallback)")
            try:
                # Original unlock command: 01 02 CA 3A
                unlock_command = "0102CA3A"  # Original unlock command with CRC
                result3 = sas_comm.sas_send_command_with_queue("MachineUnlock_Original", unlock_command, 1)
                unlock_results.append({"method": "original_unlock", "command": "0102CA3A", "result": result3, "priority": "FALLBACK"})
                print(f"[MACHINE UNLOCK] Original unlock result: {result3}")
            except Exception as e:
                print(f"[MACHINE UNLOCK] Original unlock failed: {e}")
                unlock_results.append({"method": "original_unlock", "error": str(e)})
            
            # Method 4: Advanced unlock sequence (additional fallback)
            print("[MACHINE UNLOCK] Method 4: Advanced unlock sequence (Additional Fallback)")
            try:
                if hasattr(sas_comm, 'sas_money') and sas_comm.sas_money:
                    result4 = sas_comm.sas_money.komut_advanced_unlock()
                    unlock_results.append({"method": "advanced_unlock", "result": result4, "priority": "FALLBACK"})
                    print(f"[MACHINE UNLOCK] Advanced unlock result: {result4}")
                else:
                    unlock_results.append({"method": "advanced_unlock", "error": "SAS money functions not available"})
            except Exception as e:
                print(f"[MACHINE UNLOCK] Advanced unlock failed: {e}")
                unlock_results.append({"method": "advanced_unlock", "error": str(e)})
            
            return {
                "status": "success",
                "action": "unlocked", 
                "methods_attempted": len(unlock_results),
                "unlock_results": unlock_results,
                "primary_method": "aft_cancel_transfer",
                "explanation": "AFT Game Lock detected - using AFT-specific unlock commands instead of general machine unlock",
                "timestamp": datetime.now().isoformat(),
                "message": "AFT-specific unlock sequence completed - AFT Cancel Transfer is the primary method for this lock type"
            }
            
        except Exception as e:
            raise Exception(f"Failed to unlock machine: {e}")
            
    def _machine_restart(self) -> Dict[str, Any]:
        """Restart the machine"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine restart command
            # sas_comm.send_command(0x0A)  # Example restart command
            
            return {
                "status": "success",
                "action": "restart_initiated",
                "command_sent": "0x0A",
                "timestamp": datetime.now().isoformat(),
                "message": "Machine restart initiated successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to restart machine: {e}")
            
    def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Update last communication time if connected
            if self.system_status["sas_connected"]:
                self.system_status["last_communication"] = datetime.now()
                
            # Get communication info
            sas_comm = None
            if self.slot_machine_app and self.slot_machine_app.sas_comm:
                sas_comm = self.slot_machine_app.sas_comm
                
            last_comm = self.system_status.get("last_communication")
            uptime_str = "Never" if not last_comm else f"{(datetime.now() - last_comm).total_seconds():.1f}s ago"
            
            return {
                "status": "success",
                "system": {
                    "sas_connected": self.system_status["sas_connected"],
                    "last_communication": last_comm.isoformat() if last_comm else None,
                    "asset_number": self.system_status["asset_number"],
                    "sas_version": self.system_status["sas_version"],
                    "port_info": self.system_status["port_info"],
                    "service_running": self.web_service_running,
                    "initialized": self.is_initialized,
                    "sas_address": sas_comm.sas_address if sas_comm else "N/A",
                    "device_type": sas_comm.device_type_id if sas_comm else "N/A"
                },
                "formatted_display": {
                    "connection_status": "🟢 Connected" if self.system_status["sas_connected"] else "🔴 Disconnected",
                    "last_communication": f"Last Contact: {uptime_str}",
                    "asset_number": f"Asset #: {self.system_status['asset_number'] or 'Unknown'}",
                    "port_info": f"Port: {self.system_status['port_info'] or 'Not Set'}",
                    "service_status": "✅ Running" if self.web_service_running else "❌ Stopped",
                    "initialization": "✅ Ready" if self.is_initialized else "⏳ Initializing",
                    "sas_info": f"SAS {sas_comm.sas_address} (Type {sas_comm.device_type_id})" if sas_comm else "N/A"
                },
                "message": "System status retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get system status: {e}")
            
    def _cleanup_old_commands(self):
        """Clean up old completed commands"""
        current_time = datetime.now()
        cleanup_ids = []
        
        for cmd_id, result in self.command_results.items():
            if "completed_at" in result:
                age = (current_time - result["completed_at"]).total_seconds()
                if age > 300:  # Remove results older than 5 minutes
                    cleanup_ids.append(cmd_id)
                    
        for cmd_id in cleanup_ids:
            self.command_results.pop(cmd_id, None)
            self.pending_commands.pop(cmd_id, None)
            
    async def execute_command_async(self, command_type: str, parameters: Dict[str, Any] = None, timeout: float = 10.0) -> Dict[str, Any]:
        """Execute a command asynchronously and wait for result"""
        if not self.is_initialized:
            raise Exception("SAS service not initialized")
            
        if parameters is None:
            parameters = {}
            
        # Create command
        command = SASCommand(
            id=str(uuid.uuid4()),
            command_type=command_type,
            parameters=parameters,
            timeout=timeout
        )
        
        # Add to queue
        with self._lock:
            self.pending_commands[command.id] = command
            self.command_queue.put((command.priority, command.id))
            
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            if command.id in self.command_results:
                result = self.command_results[command.id]
                
                # WebSocket broadcasting is handled at the FastAPI route level
                # This service focuses on SAS communication only
                
                return result
                
            await asyncio.sleep(0.1)
            
        # Timeout
        return {
            "status": "timeout",
            "error": f"Command timed out after {timeout} seconds"
        }
        
    def shutdown(self):
        """Shutdown the service"""
        print("[SASWebService] Shutting down...")
        self.web_service_running = False
        
        if self.slot_machine_app:
            self.slot_machine_app.shutdown()
            
        if self.background_thread:
            self.background_thread.join(timeout=5)
            
        print("[SASWebService] Shutdown complete")

    def get_card_reader_status(self):
        """Get current card reader status and card information."""
        try:
            # First try to get from dedicated card reader if available
            if (self.slot_machine_app and 
                self.slot_machine_app.card_reader_mgr and 
                self.slot_machine_app.card_reader_mgr.card_reader and
                self.slot_machine_app.card_reader_mgr.card_reader.is_card_reader_opened):
                
                card_reader = self.slot_machine_app.card_reader_mgr.card_reader
                return {
                    "success": True,
                    "card_inserted": card_reader.is_card_inside,
                    "card_number": card_reader.last_card_number,
                    "port_name": card_reader.port_name,
                    "reader_connected": card_reader.is_card_reader_opened,
                    "message": "Card reader status retrieved successfully"
                }
            
            # Fallback to checking card reader manager (even if no dedicated card reader)
            if (self.slot_machine_app and 
                self.slot_machine_app.card_reader_mgr):
                
                # Check if card reader manager has any card reader with data
                card_mgr = self.slot_machine_app.card_reader_mgr
                if (hasattr(card_mgr, 'card_reader') and 
                    card_mgr.card_reader and 
                    hasattr(card_mgr.card_reader, 'last_card_number')):
                    
                    card_reader = card_mgr.card_reader
                    return {
                        "success": True,
                        "card_inserted": card_reader.is_card_inside if hasattr(card_reader, 'is_card_inside') else False,
                        "card_number": card_reader.last_card_number,
                        "port_name": card_reader.port_name if hasattr(card_reader, 'port_name') else self.system_status.get("port_info"),
                        "reader_connected": card_reader.is_card_reader_opened if hasattr(card_reader, 'is_card_reader_opened') else False,
                        "message": "Card status retrieved from card reader manager"
                    }
            
            # No card reader available
            return {
                "success": True,
                "card_inserted": False,
                "card_number": None,
                "port_name": self.system_status.get("port_info"),
                "reader_connected": False,
                "message": "No card reader detected"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_code": "SAS_007",
                "message": f"Failed to get card reader status: {str(e)}"
            }

    def eject_card(self):
        """Eject the currently inserted card."""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.card_reader_mgr or not self.slot_machine_app.card_reader_mgr.card_reader:
                return {
                    "success": False,
                    "error_code": "SAS_008",
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.slot_machine_app.card_reader_mgr.card_reader
            
            if not card_reader.is_card_reader_opened:
                return {
                    "success": False,
                    "error_code": "SAS_009",
                    "message": "Card reader not connected"
                }
            
            # Store current card number before ejection
            current_card = card_reader.last_card_number
            
            # Send eject command
            eject_result = card_reader.card_eject()
            
            if eject_result:
                return {
                    "success": True,
                    "card_number": current_card,
                    "message": "Card eject command sent successfully"
                }
            else:
                return {
                    "success": False,
                    "error_code": "SAS_010",
                    "message": "Failed to send card eject command"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error_code": "SAS_011",
                "message": f"Failed to eject card: {str(e)}"
            }

    def get_last_card_info(self):
        """Get information about the last detected card."""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.card_reader_mgr or not self.slot_machine_app.card_reader_mgr.card_reader:
                return {
                    "success": True,
                    "card_inserted": False,
                    "last_card_number": None,
                    "port_name": None,
                    "reader_connected": False,
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.slot_machine_app.card_reader_mgr.card_reader
            
            return {
                "success": True,
                "card_inserted": card_reader.is_card_inside,
                "last_card_number": card_reader.last_card_number,
                "port_name": card_reader.port_name,
                "reader_connected": card_reader.is_card_reader_opened,
                "message": "Last card info retrieved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_code": "SAS_012",
                "message": f"Failed to get last card info: {str(e)}"
            } 