#!/usr/bin/env python3
"""
Focused AFT Registration Verification Test
This test specifically checks if AFT registration is working correctly.
"""

import sys
import time
import configparser
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from port_manager import PortManager
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

class AFTRegistrationTester:
    def __init__(self):
        # Load configuration properly like production code
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.port_mgr = PortManager()
        self.sas_comm = None
        self.running = False

    def initialize_sas(self):
        """Initialize SAS communication"""
        print("Initializing SAS communication...")
        
        # Find SAS port using production method
        sas_port, device_type = self.port_mgr.find_sas_port(self.config)
        
        if sas_port:
            print(f"Using SAS port: {sas_port}, device type: {device_type}")
            self.config.set('machine', 'devicetypeid', str(device_type))
            
            self.sas_comm = SASCommunicator(sas_port, self.config)
            if self.sas_comm.open_port():
                print("SAS communication initialized successfully!")
                
                # Trigger asset number read like production code
                self.sas_comm.send_sas_command(self.sas_comm.sas_address + '7301FF')
                time.sleep(1.0)  # Wait for asset number response
                
                # Request meters to establish communication
                print("[INFO] Requesting meters after asset number read...")
                self.sas_comm.sas_money.get_meter(isall=0)
                time.sleep(5)  # Wait for meter response
                
                return True
            else:
                print("❌ Failed to open SAS port")
                return False
        else:
            print("❌ No SAS port found")
            return False

    def start_polling(self):
        """Start background polling like production code"""
        print("🔄 Starting background polling...")
        self.running = True
        
        def poll_machine():
            if self.running and self.sas_comm:
                try:
                    # Send general poll
                    self.sas_comm.send_general_poll()
                    
                    # Check for responses
                    response = self.sas_comm.get_data_from_sas_port()
                    if response:
                        self.sas_comm.handle_received_sas_command(response)
                    
                    # Schedule next poll
                    if self.running:
                        import threading
                        threading.Timer(0.04, poll_machine).start()  # 40ms like production
                except Exception as e:
                    print(f"Polling error: {e}")
        
        # Start polling
        poll_machine()

    def stop_polling(self):
        """Stop background polling"""
        print("⏹️ Stopping background polling...")
        self.running = False

    def check_aft_status(self):
        """Check current AFT status"""
        print("\n🔍 Checking AFT Status...")
        
        # Send AFT status request
        self.sas_comm.sas_money.komut_bakiye_sorgulama("status_check", False, "aft_status_verification")
        time.sleep(2)  # Wait for response
        
        # Get status from communicator
        if hasattr(self.sas_comm, 'last_aft_status'):
            aft_status = self.sas_comm.last_aft_status
            print(f"AFT Status: {aft_status}")
            
            if aft_status:
                # Decode AFT status bits
                status_int = int(aft_status, 16)
                print(f"AFT Status Breakdown (0x{aft_status} = {status_int} = {bin(status_int)}):")
                print(f"  Bit 0 (AFT registered): {'SET' if (status_int & 0x01) else 'CLEAR'}")
                print(f"  Bit 1 (AFT enabled): {'SET' if (status_int & 0x02) else 'CLEAR'}")
                print(f"  Bit 2 (AFT transfer pending): {'SET' if (status_int & 0x04) else 'CLEAR'}")
                print(f"  Bit 3 (AFT transfer in progress): {'SET' if (status_int & 0x08) else 'CLEAR'}")
                print(f"  Bit 4 (Machine cashout mode): {'SET' if (status_int & 0x10) else 'CLEAR'}")
                print(f"  Bit 5 (Host cashout enabled): {'SET' if (status_int & 0x20) else 'CLEAR'}")
                print(f"  Bit 6 (AFT bonus mode): {'SET' if (status_int & 0x40) else 'CLEAR'}")
                print(f"  Bit 7 (Machine locked): {'SET' if (status_int & 0x80) else 'CLEAR'}")
                
                # Check if registered
                is_registered = bool(status_int & 0x01)
                is_enabled = bool(status_int & 0x02)
                
                return is_registered, is_enabled, aft_status
            else:
                print("❌ No AFT status received")
                return False, False, None
        else:
            print("❌ AFT status not available")
            return False, False, None

    def test_aft_registration(self):
        """Test AFT registration process with multiple key formats"""
        print("\n🧪 Testing AFT Registration...")
        
        # Get asset number
        asset_number = self.sas_comm.get_asset_number_for_aft()
        print(f"Using asset number: {asset_number}")
        
        # Test different registration key formats based on SAS protocol analysis
        registration_keys = [
            ("All zeros (standard)", "0000000000000000000000000000000000000000"),
            ("Empty key", ""),
            ("Asset-based key", f"{asset_number}0000000000000000000000000000000000"),
            ("Simple pattern", "1234567890ABCDEF1234567890ABCDEF12345678"),
            ("All ones", "1111111111111111111111111111111111111111"),
            ("All FF", "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"),
            ("Minimal non-zero", "0000000000000000000000000000000000000001"),
            ("Machine serial", "0000006C0000006C0000006C0000006C0000006C"),
        ]
        
        # Also try different POS IDs
        pos_ids = ["TEST01", "POS001", "TERM01", "HOST01", "SAS001"]
        
        for key_name, registration_key in registration_keys:
            for pos_id in pos_ids:
                print(f"\n🔑 Trying {key_name} with POS ID '{pos_id}': {registration_key}")
                
                # Perform AFT registration
                print("Sending AFT registration command...")
                reg_result = self.sas_comm.sas_money.komut_aft_registration(
                    asset_number, 
                    registration_key, 
                    pos_id
                )
                print(f"Registration command result: {reg_result}")
                
                # Wait for registration to process
                print("Waiting for registration to process...")
                time.sleep(2)
                
                # Check if this key worked
                is_registered, is_enabled, status = self.check_aft_status()
                if is_registered:
                    print(f"✅ SUCCESS: Registration key '{key_name}' with POS ID '{pos_id}' worked!")
                    print(f"💾 Working registration key: {registration_key}")
                    print(f"💾 Working POS ID: {pos_id}")
                    return True, registration_key
                else:
                    print(f"❌ Key '{key_name}' + POS '{pos_id}' failed (status: {status})")
                    
                # Don't test all POS IDs for empty key
                if registration_key == "":
                    break
        
        print("\n❌ All registration keys failed")
        return False, None

    def run_test(self):
        """Run the complete AFT registration verification test"""
        print("🧪 AFT Registration Verification Test")
        print("=" * 60)
        
        try:
            # Step 1: Initialize SAS
            if not self.initialize_sas():
                return False
            
            # Step 2: Start polling
            self.start_polling()
            time.sleep(2)  # Let polling stabilize
            
            # Step 3: Check initial AFT status
            print("\n📋 STEP 1: Check Initial AFT Status")
            is_registered_before, is_enabled_before, status_before = self.check_aft_status()
            
            if is_registered_before:
                print("✅ Machine is already registered for AFT")
            else:
                print("❌ Machine is NOT registered for AFT")
            
            # Step 4: Perform AFT registration
            print("\n📋 STEP 2: Perform AFT Registration")
            success, registration_key = self.test_aft_registration()
            
            # Step 5: Check AFT status after registration
            print("\n📋 STEP 3: Check AFT Status After Registration")
            is_registered_after, is_enabled_after, status_after = self.check_aft_status()
            
            # Step 6: Results analysis
            print("\n📋 STEP 4: Results Analysis")
            print("=" * 40)
            print(f"Before Registration:")
            print(f"  AFT Registered: {'YES' if is_registered_before else 'NO'}")
            print(f"  AFT Enabled: {'YES' if is_enabled_before else 'NO'}")
            print(f"  Status: {status_before}")
            print(f"")
            print(f"After Registration:")
            print(f"  AFT Registered: {'YES' if is_registered_after else 'NO'}")
            print(f"  AFT Enabled: {'YES' if is_enabled_after else 'NO'}")
            print(f"  Status: {status_after}")
            print(f"")
            
            if success:
                print("✅ SUCCESS: AFT registration worked!")
                print("💡 Machine is now ready for AFT transfers")
            elif is_registered_after and not is_registered_before:
                print("✅ SUCCESS: AFT registration worked!")
                print("💡 Machine is now ready for AFT transfers")
            elif is_registered_after and is_registered_before:
                print("ℹ️  Machine was already registered")
                print("💡 AFT transfers should work")
            elif not is_registered_after:
                print("❌ FAILURE: AFT registration did not work")
                print("💡 Possible issues:")
                print("   - Registration key mismatch")
                print("   - Asset number format incorrect")
                print("   - Machine doesn't support AFT")
                print("   - Command format issue")
            
            return success
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
        finally:
            self.stop_polling()
            if self.sas_comm:
                self.sas_comm.close_port()

def main():
    """Main test function"""
    tester = AFTRegistrationTester()
    success = tester.run_test()
    
    if success:
        print("\n🎉 AFT Registration Test PASSED")
        print("💡 You can now try AFT transfers")
    else:
        print("\n❌ AFT Registration Test FAILED")
        print("💡 AFT transfers will not work until registration is fixed")

if __name__ == "__main__":
    main() 