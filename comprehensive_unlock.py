#!/usr/bin/env python3
"""
Comprehensive Machine Unlock Tool
Attempts multiple SAS unlock strategies and provides detailed diagnostics
"""

import asyncio
import time
import threading
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager
from utils import get_crc

class ComprehensiveUnlocker:
    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator = None
        
    def start_polling(self):
        """Start background polling thread"""
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        print("✅ Background polling started")
        
    def stop_polling(self):
        """Stop background polling"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1)
        print("✅ Background polling stopped")
        
    def _poll_loop(self):
        """Background polling loop"""
        while self.running:
            if self.communicator and self.communicator.is_port_open:
                try:
                    self.communicator.send_general_poll()
                    time.sleep(0.05)
                    response = self.communicator.get_data_from_sas_port()
                    if response:
                        print(f"RX: {response}")
                        self.communicator.handle_received_sas_command(response)
                except Exception as e:
                    print(f"Poll error: {e}")
            time.sleep(0.04)

    def decode_lock_status(self, lock_status_hex):
        """Decode lock status bits"""
        if not lock_status_hex:
            return "Unknown"
            
        try:
            status = int(lock_status_hex, 16)
            locks = []
            
            if status & 0x01: locks.append("Gaming Machine Disabled")
            if status & 0x02: locks.append("Progressive Lockup")
            if status & 0x04: locks.append("Machine Tilt")
            if status & 0x08: locks.append("Cash Door Open")
            if status & 0x10: locks.append("Logic Door Open")
            if status & 0x20: locks.append("Bill Acceptor Door Open")
            if status & 0x40: locks.append("Memory Error")
            if status & 0x80: locks.append("Gaming Locked")
            
            if not locks:
                return "No locks (machine should be operational)"
            
            return f"Active locks: {', '.join(locks)}"
            
        except:
            return f"Could not decode: {lock_status_hex}"

    def send_sas_command_with_response(self, command_name, command, expected_length=None, timeout=2):
        """Send SAS command and wait for response"""
        print(f"[{command_name}] Sending: {command}")
        
        try:
            # Clear any pending data
            self.communicator.get_data_from_sas_port()
            
            # Send command
            self.communicator.send_sas_command(command)
            
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout:
                response = self.communicator.get_data_from_sas_port()
                if response:
                    print(f"[{command_name}] Response: {response}")
                    return response
                time.sleep(0.05)
                
            print(f"[{command_name}] No response within {timeout}s")
            return None
            
        except Exception as e:
            print(f"[{command_name}] Error: {e}")
            return None

    def comprehensive_unlock_sequence(self):
        """Try comprehensive unlock sequence"""
        print("\n🔧 === COMPREHENSIVE UNLOCK SEQUENCE ===")
        
        # Step 1: Get current status
        print("\n--- Step 1: Current Status Analysis ---")
        balance_response = self.communicator.sas_money.komut_bakiye_sorgulama(
            sender="comprehensive_unlock", 
            isforinfo=False, 
            sendertext="status_check"
        )
        
        if hasattr(self.communicator, 'game_lock_status'):
            lock_status = getattr(self.communicator, 'game_lock_status', 'Unknown')
            print(f"Current Lock Status: {lock_status}")
            print(f"Lock Analysis: {self.decode_lock_status(lock_status)}")
        
        # Step 2: Try basic machine enable/disable cycle
        print("\n--- Step 2: Machine Enable/Disable Cycle ---")
        
        # Disable machine
        disable_cmd = self.communicator.sas_address + "8D"
        disable_crc = get_crc(disable_cmd)
        self.send_sas_command_with_response("DISABLE", disable_crc)
        time.sleep(1)
        
        # Enable machine
        enable_cmd = self.communicator.sas_address + "8E"
        enable_crc = get_crc(enable_cmd)
        self.send_sas_command_with_response("ENABLE", enable_crc)
        time.sleep(1)
        
        # Step 3: Try different unlock commands
        print("\n--- Step 3: Multiple Unlock Approaches ---")
        
        asset_number = getattr(self.communicator, 'asset_number_aft_format', '0000006C')
        
        unlock_commands = [
            # Standard unlock with all zeros
            ("UNLOCK_ALL_ZEROS", f"{self.communicator.sas_address}74{asset_number}00000000"),
            
            # Unlock with FF (all bits)
            ("UNLOCK_ALL_FF", f"{self.communicator.sas_address}74{asset_number}00FF0000"),
            
            # Unlock specific lock bits
            ("UNLOCK_GAMING", f"{self.communicator.sas_address}74{asset_number}00800000"),  # Gaming lock only
            ("UNLOCK_DOORS", f"{self.communicator.sas_address}74{asset_number}00380000"),   # Door locks
            ("UNLOCK_TILT", f"{self.communicator.sas_address}74{asset_number}00040000"),    # Tilt lock
            
            # Alternative unlock format
            ("UNLOCK_ALT1", f"{self.communicator.sas_address}74{asset_number}FF000000"),
            ("UNLOCK_ALT2", f"{self.communicator.sas_address}74{asset_number}FFFF0000"),
        ]
        
        for cmd_name, cmd in unlock_commands:
            cmd_crc = get_crc(cmd)
            response = self.send_sas_command_with_response(cmd_name, cmd_crc)
            time.sleep(0.5)
            
            # Check status after each attempt
            balance_response = self.communicator.sas_money.komut_bakiye_sorgulama(
                sender="unlock_verify", 
                isforinfo=True, 
                sendertext=f"after_{cmd_name.lower()}"
            )
            
            if hasattr(self.communicator, 'game_lock_status'):
                current_status = getattr(self.communicator, 'game_lock_status', 'Unknown')
                print(f"  Status after {cmd_name}: {current_status}")
                if current_status != 'FF':
                    print(f"  🎉 SUCCESS! Lock status changed to: {current_status}")
                    break
            
            time.sleep(1)
        
        # Step 4: Try host control clearing
        print("\n--- Step 4: Host Control Management ---")
        
        # Clear host cashout enable
        clear_host_cmd = self.communicator.sas_address + "85"
        clear_host_crc = get_crc(clear_host_cmd)
        self.send_sas_command_with_response("CLEAR_HOST_CONTROLS", clear_host_crc)
        time.sleep(1)
        
        # Step 5: Try reservation clearing
        print("\n--- Step 5: Reservation Management ---")
        
        # Clear reservation
        clear_res_cmd = self.communicator.sas_address + "8F"
        clear_res_crc = get_crc(clear_res_cmd)
        self.send_sas_command_with_response("CLEAR_RESERVATION", clear_res_crc)
        time.sleep(1)
        
        # Step 6: Try legacy unlock commands
        print("\n--- Step 6: Legacy Unlock Commands ---")
        
        legacy_commands = [
            # Send gaming machine ID and info (might reset some states)
            ("MACHINE_ID", f"{self.communicator.sas_address}1F"),
            
            # Request SAS version (sometimes helps with state)
            ("SAS_VERSION", f"{self.communicator.sas_address}54"),
            
            # Send selected meter for game (might clear some locks)
            ("METER_REQUEST", f"{self.communicator.sas_address}AF1A0000A000B8"),
        ]
        
        for cmd_name, cmd in legacy_commands:
            cmd_crc = get_crc(cmd)
            self.send_sas_command_with_response(cmd_name, cmd_crc)
            time.sleep(0.5)
        
        # Step 7: Final status check
        print("\n--- Step 7: Final Status Check ---")
        final_response = self.communicator.sas_money.komut_bakiye_sorgulama(
            sender="final_check", 
            isforinfo=False, 
            sendertext="comprehensive_unlock_final"
        )
        
        if hasattr(self.communicator, 'game_lock_status'):
            final_status = getattr(self.communicator, 'game_lock_status', 'Unknown')
            print(f"Final Lock Status: {final_status}")
            print(f"Final Analysis: {self.decode_lock_status(final_status)}")
            
            if final_status == 'FF':
                print("❌ UNLOCK FAILED: Machine remains fully locked")
                print("\n🔍 RECOMMENDATIONS:")
                print("1. Check physical door switches (cash door, logic door, bill acceptor door)")
                print("2. Check for machine tilt condition")
                print("3. Verify machine power cycle")
                print("4. Check for memory errors")
                print("5. May require technician intervention")
                return False
            else:
                print(f"✅ PARTIAL SUCCESS: Lock status changed to {final_status}")
                return True
        
        return False

    def run_comprehensive_unlock(self):
        """Main unlock process"""
        print("=== Comprehensive Machine Unlock Tool ===")
        print("This tool attempts multiple SAS unlock strategies")
        
        # Initialize SAS communication
        config = ConfigManager()
        port = "/dev/ttyUSB1"  # Adjust as needed
        
        print(f"Using port: {port}")
        print("Opening SAS port...")
        
        self.communicator = SASCommunicator(port, config)
        
        if not self.communicator.open_port():
            print("❌ Failed to open SAS port")
            return False
        
        print("✅ SAS port opened successfully")
        
        # Start background polling
        self.start_polling()
        
        try:
            print("Waiting for initial communication to stabilize...")
            time.sleep(3)
            
            # Run comprehensive unlock
            success = self.comprehensive_unlock_sequence()
            
            print(f"\n=== FINAL RESULT ===")
            if success:
                print("✅ Machine unlock completed successfully!")
            else:
                print("❌ Machine unlock failed - may require physical intervention")
            
            return success
            
        finally:
            print("\nCleaning up...")
            self.stop_polling()
            if self.communicator:
                self.communicator.close_port()
            print("✅ Port closed")

if __name__ == "__main__":
    unlocker = ComprehensiveUnlocker()
    unlocker.run_comprehensive_unlock() 