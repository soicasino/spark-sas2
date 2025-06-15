#!/usr/bin/env python3
"""
Lock/Unlock Test with Real-time Status Monitoring
Tests the original lock/unlock commands while monitoring machine status
"""

import time
import threading
import requests
import json
from sas_communicator import SASCommunicator
from config_manager import ConfigManager

class LockUnlockMonitor:
    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator = None
        self.api_base = "http://10.0.0.200:8000/api"
        
    def get_machine_status(self):
        """Get current machine status via API"""
        try:
            response = requests.get(f"{self.api_base}/machine/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', {})
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        return None
    
    def print_status(self, label="Status"):
        """Print current machine status"""
        status = self.get_machine_status()
        if status:
            lock_status = status.get('lock_status', 'Unknown')
            aft_status = status.get('aft_status', 'Unknown')
            is_locked = status.get('is_locked', 'Unknown')
            available_transfers = status.get('available_transfers', 'Unknown')
            
            print(f"\n📊 {label}:")
            print(f"   Lock Status: {lock_status} ({'🔒 LOCKED' if lock_status == 'FF' else '🔓 UNLOCKED' if lock_status == '00' else '🔄 PARTIAL'})")
            print(f"   AFT Status: {aft_status}")
            print(f"   Is Locked: {is_locked}")
            print(f"   Available Transfers: {available_transfers}")
            
            return lock_status
        else:
            print(f"\n❌ {label}: Could not retrieve status")
            return None
    
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
            self.poll_thread.join(timeout=2)
        print("✅ Background polling stopped")
        
    def _poll_loop(self):
        """Background polling loop"""
        while self.running:
            try:
                if self.communicator and self.communicator.is_port_open:
                    # Simple polling - just keep connection alive
                    time.sleep(0.1)
                else:
                    time.sleep(0.5)
            except Exception as e:
                if self.running:
                    print(f"Polling error: {e}")
                time.sleep(1)

    def send_command_direct(self, command_name, command_hex):
        """Send a SAS command directly"""
        try:
            print(f"\n🔧 [{command_name}] Sending: {command_hex}")
            
            # Send the command using the communicator's direct method
            result = self.communicator.sas_send_command_with_queue(
                command_name, 
                command_hex, 
                0  # do_save_db parameter
            )
            
            print(f"   Command sent, waiting for effect...")
            time.sleep(1)  # Give time for command to take effect
            
            return True
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def test_unlock_sequence(self):
        """Test unlock with multiple approaches"""
        print("\n🔓 === COMPREHENSIVE UNLOCK TEST ===")
        
        # Method 1: Original unlock command (twice)
        print("\n--- Method 1: Original Unlock Command (0102CA3A) ---")
        initial_status = self.print_status("Before Unlock")
        
        # Send unlock command twice like in original code
        self.send_command_direct("UNLOCK_1", "0102CA3A")
        time.sleep(0.1)
        self.send_command_direct("UNLOCK_2", "0102CA3A")
        time.sleep(2)
        
        after_unlock = self.print_status("After Original Unlock")
        
        # Check if status changed
        if initial_status != after_unlock:
            print("✅ Status changed after unlock!")
        else:
            print("❌ No status change detected")
            
        return after_unlock
    
    def test_lock_sequence(self):
        """Test lock command"""
        print("\n🔒 === LOCK TEST ===")
        
        initial_status = self.print_status("Before Lock")
        
        # Send lock command
        self.send_command_direct("LOCK", "01015108")
        time.sleep(2)
        
        after_lock = self.print_status("After Lock")
        
        # Check if status changed
        if initial_status != after_lock:
            print("✅ Status changed after lock!")
        else:
            print("❌ No status change detected")
            
        return after_lock
    
    def test_alternative_unlocks(self):
        """Test alternative unlock approaches"""
        print("\n🔧 === ALTERNATIVE UNLOCK METHODS ===")
        
        # Method 2: Try different unlock variations
        unlock_commands = [
            ("UNLOCK_ALT_1", "01020000"),  # Simple unlock without CRC
            ("UNLOCK_ALT_2", "010200CA3A"),  # With extra bytes
            ("UNLOCK_ALT_3", "01020001"),  # Different parameter
        ]
        
        for cmd_name, cmd_hex in unlock_commands:
            print(f"\n--- Testing {cmd_name}: {cmd_hex} ---")
            before = self.print_status(f"Before {cmd_name}")
            
            self.send_command_direct(cmd_name, cmd_hex)
            time.sleep(2)
            
            after = self.print_status(f"After {cmd_name}")
            
            if before != after:
                print(f"✅ {cmd_name} caused status change!")
                return True
            else:
                print(f"❌ {cmd_name} - no change")
        
        return False
    
    def run_comprehensive_test(self):
        """Run comprehensive lock/unlock test with monitoring"""
        print("=== Lock/Unlock Test with Real-time Monitoring ===")
        print("This test monitors machine status while testing lock/unlock commands")
        
        # Initialize SAS communication
        config = ConfigManager()
        port = "/dev/ttyUSB1"
        
        print(f"\nUsing port: {port}")
        print("Opening SAS port...")
        
        self.communicator = SASCommunicator(port, config)
        
        if not self.communicator.open_port():
            print("❌ Failed to open SAS port")
            return False
        
        print("✅ SAS port opened successfully")
        
        # Start background polling
        self.start_polling()
        
        try:
            print("\nWaiting for communication to stabilize...")
            time.sleep(3)
            
            # Initial status
            print("\n" + "="*50)
            initial_status = self.print_status("INITIAL STATUS")
            print("="*50)
            
            # Test unlock first
            unlock_status = self.test_unlock_sequence()
            
            # If unlock didn't work, try alternatives
            if unlock_status == 'FF':  # Still locked
                print("\n⚠️  Original unlock didn't work, trying alternatives...")
                self.test_alternative_unlocks()
            
            # Test lock (if machine got unlocked)
            current_status = self.print_status("Current Status")
            if current_status != 'FF':  # If not fully locked
                lock_status = self.test_lock_sequence()
                
                # Try unlock again after lock
                if lock_status == 'FF':  # If successfully locked
                    print("\n🔄 Testing unlock after successful lock...")
                    self.test_unlock_sequence()
            
            # Final status
            print("\n" + "="*50)
            final_status = self.print_status("FINAL STATUS")
            print("="*50)
            
            # Summary
            print("\n📋 === TEST SUMMARY ===")
            print(f"Initial Status: {initial_status}")
            print(f"Final Status: {final_status}")
            
            if initial_status != final_status:
                print("✅ Machine status changed during testing!")
                print("   This indicates the commands are having some effect.")
            else:
                print("❌ No status changes detected")
                print("   The machine may require different commands or conditions.")
                
            return True
            
        finally:
            print("\nCleaning up...")
            self.stop_polling()
            if self.communicator:
                self.communicator.close_port()
            print("✅ Port closed")

if __name__ == "__main__":
    tester = LockUnlockMonitor()
    tester.run_comprehensive_test() 