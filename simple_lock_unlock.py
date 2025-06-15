#!/usr/bin/env python3
"""
Simple Lock/Unlock Script
Uses the original working commands from raspberryPython_orj.py
"""

import time
import threading
from sas_communicator import SASCommunicator
from config_manager import ConfigManager

class SimpleLockUnlock:
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
            self.poll_thread.join(timeout=2)
        print("✅ Background polling stopped")
        
    def _poll_loop(self):
        """Background polling loop"""
        while self.running:
            try:
                if self.communicator and self.communicator.is_open:
                    # Simple general poll
                    response = self.communicator.read_data(timeout=0.1)
                    if response:
                        print(f"RX: {response}")
                time.sleep(0.1)
            except Exception as e:
                if self.running:  # Only print if we're still supposed to be running
                    print(f"Polling error: {e}")
                time.sleep(0.5)

    def send_command(self, command_name, command_hex):
        """Send a SAS command and wait for response"""
        try:
            print(f"[{command_name}] Sending command: {command_hex}")
            
            # Send the command
            result = self.communicator.sas_send_command_with_queue(
                command_name, 
                command_hex, 
                expected_length=1  # Expecting simple ACK
            )
            
            if result:
                print(f"[{command_name}] Response: {result}")
                return result
            else:
                print(f"[{command_name}] No response received")
                return None
                
        except Exception as e:
            print(f"[{command_name}] Error: {e}")
            return None

    def lock_machine(self):
        """Lock the gaming machine using original command"""
        print("\\n🔒 === LOCKING MACHINE ===")
        print("Using original command from raspberryPython_orj.py")
        
        # Original lock command: 01 01 51 08
        command = "01015108"
        response = self.send_command("LOCK_MACHINE", command)
        
        if response:
            print("✅ Lock command sent successfully")
            print("Machine should now be locked")
        else:
            print("❌ Lock command failed")
            
        return response is not None

    def unlock_machine(self):
        """Unlock the gaming machine using original command"""
        print("\\n🔓 === UNLOCKING MACHINE ===")
        print("Using original command from raspberryPython_orj.py")
        
        # Original unlock command: 01 02 CA 3A
        command = "0102CA3A"
        
        # Send twice like in original code
        print("Sending unlock command (attempt 1)...")
        response1 = self.send_command("UNLOCK_MACHINE_1", command)
        time.sleep(0.1)
        
        print("Sending unlock command (attempt 2)...")
        response2 = self.send_command("UNLOCK_MACHINE_2", command)
        
        if response1 or response2:
            print("✅ Unlock command sent successfully")
            print("Machine should now be unlocked")
        else:
            print("❌ Unlock command failed")
            
        return response1 is not None or response2 is not None

    def check_machine_status(self):
        """Check current machine status"""
        print("\\n📊 === CHECKING MACHINE STATUS ===")
        
        try:
            # Use the balance query to check status
            if hasattr(self.communicator, 'sas_money'):
                balance_response = self.communicator.sas_money.komut_bakiye_sorgulama(
                    sender="status_check", 
                    isforinfo=True, 
                    sendertext="simple_lock_unlock_status"
                )
                
                if hasattr(self.communicator, 'game_lock_status'):
                    lock_status = getattr(self.communicator, 'game_lock_status', 'Unknown')
                    print(f"Current Lock Status: {lock_status}")
                    
                    if lock_status == 'FF':
                        print("🔒 Machine is LOCKED (all lock bits active)")
                    elif lock_status == '00':
                        print("🔓 Machine is UNLOCKED")
                    else:
                        print(f"🔄 Machine has partial locks: {lock_status}")
                        
                    return lock_status
                else:
                    print("❌ Could not read lock status")
            else:
                print("❌ SAS Money service not available")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            
        return None

    def run_test_sequence(self):
        """Run a complete test sequence"""
        print("=== Simple Lock/Unlock Test ===")
        print("Using original commands from raspberryPython_orj.py")
        
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
            print("Waiting for communication to stabilize...")
            time.sleep(3)
            
            # Check initial status
            print("\\n=== INITIAL STATUS ===")
            initial_status = self.check_machine_status()
            
            # Test unlock first (in case it's already locked)
            print("\\n=== STEP 1: UNLOCK TEST ===")
            unlock_success = self.unlock_machine()
            time.sleep(2)
            
            # Check status after unlock
            unlock_status = self.check_machine_status()
            
            # Test lock
            print("\\n=== STEP 2: LOCK TEST ===")
            lock_success = self.lock_machine()
            time.sleep(2)
            
            # Check status after lock
            lock_status = self.check_machine_status()
            
            # Test unlock again
            print("\\n=== STEP 3: UNLOCK TEST (AGAIN) ===")
            unlock_success2 = self.unlock_machine()
            time.sleep(2)
            
            # Final status check
            final_status = self.check_machine_status()
            
            # Summary
            print("\\n=== TEST SUMMARY ===")
            print(f"Initial Status: {initial_status}")
            print(f"After Unlock: {unlock_status}")
            print(f"After Lock: {lock_status}")
            print(f"Final Status: {final_status}")
            
            if unlock_success and lock_success and unlock_success2:
                print("✅ All commands executed successfully!")
            else:
                print("❌ Some commands failed")
                
            return True
            
        finally:
            print("\\nCleaning up...")
            self.stop_polling()
            if self.communicator:
                self.communicator.close_port()
            print("✅ Port closed")

if __name__ == "__main__":
    tester = SimpleLockUnlock()
    tester.run_test_sequence() 