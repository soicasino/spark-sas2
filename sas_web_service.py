"""
SAS Web Service - Thread-safe wrapper for SAS communication
Provides a bridge between FastAPI endpoints and the core SAS system
"""
import threading
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import uuid
import queue

from slot_machine_application import SlotMachineApplication
from websocket_manager import websocket_manager


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
        """Get meter information and return parsed results"""
        try:
            sas_money = self.slot_machine_app.sas_comm.sas_money
            
            # Clear any previous meter data
            sas_money.last_parsed_meters = {}
            
            # Send the appropriate meter command
            if meter_type == "basic":
                sas_money.get_meter(isall=0)
            elif meter_type == "extended":
                sas_money.get_meter(isall=2)
            elif meter_type == "all":
                sas_money.get_meter(isall=1)
            else:
                raise Exception(f"Unknown meter type: {meter_type}")
            
            # Wait for response processing
            max_wait = 8  # seconds
            wait_time = 0
            while wait_time < max_wait:
                time.sleep(0.3)
                wait_time += 0.3
                
                # Check if we got meter data
                if hasattr(sas_money, 'last_parsed_meters') and sas_money.last_parsed_meters:
                    break
            
            # Get the parsed meters
            parsed_meters = getattr(sas_money, 'last_parsed_meters', {})
            
            # Format response
            if parsed_meters:
                return {
                    "meter_type": meter_type,
                    "status": "success",
                    "meters": parsed_meters,
                    "message": f"Successfully retrieved {len(parsed_meters)} meter values",
                    "formatted_display": self._format_meters_for_display(parsed_meters)
                }
            else:
                return {
                    "meter_type": meter_type,
                    "status": "no_data",
                    "message": "Meter command sent but no response received within timeout",
                    "meters": {},
                    "note": "Check SAS communication and slot machine connection"
                }
            
        except Exception as e:
            raise Exception(f"Failed to get meters: {e}")
    
    def _format_meters_for_display(self, meters: Dict[str, float]) -> Dict[str, str]:
        """Format meter values for human-readable display"""
        formatted = {}
        
        for meter_name, value in meters.items():
            if meter_name in ['total_turnover', 'total_win', 'total_jackpot', 'current_credits', 
                             'total_ticket_in', 'total_ticket_out', 'total_electronic_in', 
                             'total_electronic_out', 'total_bonus', 'total_coin_in', 'total_coin_out']:
                # Money values
                formatted[meter_name] = f"{value:,.2f} TL"
            elif meter_name in ['games_played', 'games_won', 'bills_accepted']:
                # Count values
                formatted[meter_name] = f"{int(value):,}"
            else:
                # Default formatting
                formatted[meter_name] = f"{value:,.2f}"
                
        return formatted
            
    def _get_balance(self) -> Dict[str, Any]:
        """Get current balance with formatted display"""
        try:
            sas_money = self.slot_machine_app.sas_comm.sas_money
            
            # Send balance query
            self.slot_machine_app.sas_comm.money_balance_query("WebAPI", True)
            time.sleep(2)  # Wait for response
            
            # Get raw balance values
            cashable = float(sas_money.yanit_bakiye_tutar)
            restricted = float(sas_money.yanit_restricted_amount) 
            nonrestricted = float(sas_money.yanit_nonrestricted_amount)
            total_balance = cashable + restricted + nonrestricted
            
            return {
                "status": "success",
                "balance": {
                    "cashable_amount": cashable,
                    "restricted_amount": restricted,
                    "nonrestricted_amount": nonrestricted,
                    "total_balance": total_balance
                },
                "formatted_display": {
                    "cashable_amount": f"{cashable:,.2f} TL",
                    "restricted_amount": f"{restricted:,.2f} TL", 
                    "nonrestricted_amount": f"{nonrestricted:,.2f} TL",
                    "total_balance": f"{total_balance:,.2f} TL"
                },
                "message": "Balance retrieved successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get balance: {e}")
            
    def _get_sas_version(self) -> Dict[str, Any]:
        """Get SAS version with formatted display"""
        try:
            # Send SAS version request
            self.slot_machine_app.sas_comm.request_sas_version()
            time.sleep(2)  # Wait for response
            
            # Try to get response from recent communication
            # Note: You may need to implement version storage in your SAS communicator
            sas_comm = self.slot_machine_app.sas_comm
            
            return {
                "status": "success", 
                "version_info": {
                    "command_sent": True,
                    "sas_address": sas_comm.sas_address,
                    "device_type_id": sas_comm.device_type_id,
                    "port_name": sas_comm.port_name,
                    "baud_rate": sas_comm.baud_rate
                },
                "formatted_display": {
                    "sas_address": f"Address: {sas_comm.sas_address}",
                    "device_type": f"Device Type: {sas_comm.device_type_id}",
                    "connection": f"Port: {sas_comm.port_name} @ {sas_comm.baud_rate} baud",
                    "status": "✅ SAS Version Request Sent"
                },
                "message": "SAS version request sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get SAS version: {e}")
            
    def _get_asset_number(self) -> Dict[str, Any]:
        """Get asset number with formatted display"""
        try:
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send asset number request
            command = sas_comm.sas_address + '7301FF'
            from utils import get_crc
            command_crc = get_crc(command)
            sas_comm.sas_send_command_with_queue('ReadAssetNo', command_crc, 0)
            time.sleep(2)  # Wait for response
            
            # Get system status for asset number if available
            asset_number = self.system_status.get("asset_number", "Pending...")
            
            return {
                "status": "success",
                "asset_info": {
                    "command_sent": True,
                    "asset_number": asset_number,
                    "sas_address": sas_comm.sas_address,
                    "port_info": sas_comm.port_name
                },
                "formatted_display": {
                    "asset_number": f"Asset #: {asset_number}",
                    "sas_address": f"SAS Address: {sas_comm.sas_address}",
                    "port": f"Connected to: {sas_comm.port_name}",
                    "status": "✅ Asset Number Request Sent"
                },
                "message": "Asset number request sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get asset number: {e}")
            
    def _bill_acceptor_control(self, enable: bool) -> Dict[str, Any]:
        """Enable or disable bill acceptor with formatted display"""
        try:
            if not hasattr(self.slot_machine_app.sas_comm, 'bill_acceptor'):
                raise Exception("Bill acceptor not available")
                
            bill_acceptor = self.slot_machine_app.sas_comm.bill_acceptor
            
            if enable:
                bill_acceptor.bill_acceptor_inhibit_open()
                action = "enabled"
                action_verb = "Enable"
                status_icon = "✅"
            else:
                bill_acceptor.bill_acceptor_inhibit_close()
                action = "disabled"
                action_verb = "Disable"
                status_icon = "🚫"
                
            return {
                "status": "success",
                "bill_acceptor": {
                    "action": action,
                    "enabled": enable,
                    "is_open": bill_acceptor.is_billacceptor_open,
                    "device_type": bill_acceptor.g_machine_bill_acceptor_type_id
                },
                "formatted_display": {
                    "action": f"{status_icon} Bill Acceptor {action.title()}",
                    "status": f"Status: {action.upper()}",
                    "device": f"Device Type: {bill_acceptor.g_machine_bill_acceptor_type_id}",
                    "operation": f"{action_verb} command sent successfully"
                },
                "message": f"Bill acceptor {action} successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to control bill acceptor: {e}")
            
    def _machine_lock(self) -> Dict[str, Any]:
        """Lock the machine with formatted display"""
        try:
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine lock command (you may need to implement specific lock commands)
            # For now, using a general approach - customize based on your SAS commands
            lock_command = sas_comm.sas_address + "7400" + "9000"  # Lock code 00, timeout 9000
            from utils import get_crc
            command_crc = get_crc(lock_command)
            sas_comm.sas_send_command_with_queue('MachineLock', command_crc, 1)
            
            return {
                "status": "success",
                "machine_control": {
                    "action": "lock",
                    "locked": True,
                    "sas_address": sas_comm.sas_address,
                    "command_sent": True
                },
                "formatted_display": {
                    "action": "🔒 Machine Locked",
                    "status": "Status: LOCKED",
                    "sas_info": f"SAS Address: {sas_comm.sas_address}",
                    "operation": "Lock command sent successfully"
                },
                "message": "Machine lock command sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to lock machine: {e}")
            
    def _machine_unlock(self) -> Dict[str, Any]:
        """Unlock the machine with formatted display"""
        try:
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine unlock command (you may need to implement specific unlock commands)
            # For now, using a general approach - customize based on your SAS commands
            unlock_command = sas_comm.sas_address + "7400" + "0000"  # Lock code 00, timeout 0000 (unlock)
            from utils import get_crc
            command_crc = get_crc(unlock_command)
            sas_comm.sas_send_command_with_queue('MachineUnlock', command_crc, 1)
            
            return {
                "status": "success",
                "machine_control": {
                    "action": "unlock",
                    "locked": False,
                    "sas_address": sas_comm.sas_address,
                    "command_sent": True
                },
                "formatted_display": {
                    "action": "🔓 Machine Unlocked",
                    "status": "Status: UNLOCKED",
                    "sas_info": f"SAS Address: {sas_comm.sas_address}",
                    "operation": "Unlock command sent successfully"
                },
                "message": "Machine unlock command sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to unlock machine: {e}")
    
    def _machine_restart(self) -> Dict[str, Any]:
        """Restart the machine with formatted display"""
        try:
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine restart command (implement specific restart commands based on your SAS protocol)
            # This is a generic example - customize based on your machine's restart procedure
            restart_command = sas_comm.sas_address + "7F"  # Machine restart command
            from utils import get_crc
            command_crc = get_crc(restart_command)
            sas_comm.sas_send_command_with_queue('MachineRestart', command_crc, 1)
            
            return {
                "status": "success",
                "machine_control": {
                    "action": "restart",
                    "restart_initiated": True,
                    "sas_address": sas_comm.sas_address,
                    "command_sent": True
                },
                "formatted_display": {
                    "action": "🔄 Machine Restart Initiated",
                    "status": "Status: RESTARTING",
                    "sas_info": f"SAS Address: {sas_comm.sas_address}",
                    "operation": "Restart command sent successfully",
                    "warning": "⚠️ Machine will be unavailable during restart"
                },
                "message": "Machine restart command sent successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to restart machine: {e}")
            
    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status with formatted display"""
        try:
            sas_comm = self.slot_machine_app.sas_comm if self.slot_machine_app else None
            last_comm = self.system_status["last_communication"]
            
            # Calculate uptime
            from datetime import datetime
            if last_comm:
                uptime_seconds = (datetime.now() - last_comm).total_seconds()
                uptime_str = f"{int(uptime_seconds // 60)} minutes ago"
            else:
                uptime_str = "Never"
            
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
                
                # Broadcast to WebSocket clients if this is a relevant update
                try:
                    if command_type in ["get_meters", "get_balance"]:
                        # Import here to avoid circular imports
                        await connection_manager.broadcast_to_subscribed("meters", result)
                    elif command_type == "system_status":
                        from websocket_manager import connection_manager
                        await connection_manager.broadcast_to_subscribed("system_status", result)
                    elif command_type in ["machine_lock", "machine_unlock", "machine_restart"]:
                        from websocket_manager import connection_manager
                        await connection_manager.broadcast_to_subscribed("machine_events", result)
                    elif command_type in ["bill_acceptor_enable", "bill_acceptor_disable"]:
                        from websocket_manager import connection_manager
                        await connection_manager.broadcast_to_subscribed("bill_events", result)
                except Exception as e:
                    print(f"[SASWebService] Error broadcasting WebSocket update: {e}")
                
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
            if not self.app or not self.app.card_reader_mgr or not self.app.card_reader_mgr.card_reader:
                return {
                    "success": True,
                    "card_inserted": False,
                    "card_number": None,
                    "port_name": None,
                    "reader_connected": False,
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.app.card_reader_mgr.card_reader
            
            return {
                "success": True,
                "card_inserted": card_reader.is_card_inside,
                "card_number": card_reader.last_card_number,
                "port_name": card_reader.port_name,
                "reader_connected": card_reader.is_card_reader_opened,
                "message": "Card reader status retrieved successfully"
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
            if not self.app or not self.app.card_reader_mgr or not self.app.card_reader_mgr.card_reader:
                return {
                    "success": False,
                    "error_code": "SAS_008",
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.app.card_reader_mgr.card_reader
            
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
            if not self.app or not self.app.card_reader_mgr or not self.app.card_reader_mgr.card_reader:
                return {
                    "success": True,
                    "card_inserted": False,
                    "last_card_number": None,
                    "port_name": None,
                    "reader_connected": False,
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.app.card_reader_mgr.card_reader
            
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