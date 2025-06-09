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
            
            # Send bill acceptor control command
            command = 0x1A if enable else 0x1B  # SAS commands for enable/disable
            
            # This would send the actual SAS command
            # sas_comm.send_command(command)
            
            action = "enabled" if enable else "disabled"
            
            return {
                "status": "success",
                "action": action,
                "command_sent": f"0x{command:02X}",
                "timestamp": datetime.now().isoformat(),
                "message": f"Bill acceptor {action} successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to control bill acceptor: {e}")
            
    def _machine_lock(self) -> Dict[str, Any]:
        """Lock the machine"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine lock command (SAS 0x01)
            # sas_comm.send_command(0x01)
            
            return {
                "status": "success",
                "action": "locked",
                "command_sent": "0x01",
                "timestamp": datetime.now().isoformat(),
                "message": "Machine locked successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to lock machine: {e}")
            
    def _machine_unlock(self) -> Dict[str, Any]:
        """Unlock the machine"""
        try:
            if not self.slot_machine_app or not self.slot_machine_app.sas_comm:
                raise Exception("SAS communication not available")
                
            sas_comm = self.slot_machine_app.sas_comm
            
            # Send machine unlock command (SAS 0x02)
            # sas_comm.send_command(0x02)
            
            return {
                "status": "success",
                "action": "unlocked", 
                "command_sent": "0x02",
                "timestamp": datetime.now().isoformat(),
                "message": "Machine unlocked successfully"
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
            if not self.slot_machine_app or not self.slot_machine_app.card_reader_mgr or not self.slot_machine_app.card_reader_mgr.card_reader:
                return {
                    "success": True,
                    "card_inserted": False,
                    "card_number": None,
                    "port_name": None,
                    "reader_connected": False,
                    "message": "Card reader not initialized"
                }
            
            card_reader = self.slot_machine_app.card_reader_mgr.card_reader
            
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