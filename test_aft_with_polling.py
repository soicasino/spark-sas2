#!/usr/bin/env python3
"""
Test AFT transfers using the EXACT production code pattern.
This mimics how the main application works with proper port finding and polling.
"""

import sys
import time
import threading
import os
import configparser

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from port_manager import PortManager
from sas_communicator import SASCommunicator

class ProductionStyleAFTTester:
    """AFT tester that follows the exact production code pattern"""
    
    def __init__(self):
        # Load configuration properly like production code
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.port_mgr = PortManager()  # PortManager doesn't take config in constructor
        self.sas_comm = None
        self.running = False
        self.sas_poll_timer = None
        
    def initialize_sas(self):
        """Initialize SAS communication - EXACT copy from production code"""
        print("Initializing SAS communication...")
        
        # Find SAS port using production method
        sas_port, device_type = self.port_mgr.find_sas_port(self.config)
        
        if sas_port:
            print(f"Using SAS port: {sas_port}, device type: {device_type}")
            
            # Create SAS communicator with proper config
            self.sas_comm = SASCommunicator(sas_port, self.config)
            if self.sas_comm.open_port():
                print("SAS communication initialized successfully!")
                
                # Trigger asset number read like production code
                self.sas_comm.send_sas_command(self.sas_comm.sas_address + '7301FF')
                time.sleep(1.0)  # Wait for asset number response
                
                # Request meters like production code
                print("[INFO] Requesting meters after asset number read...")
                self.sas_comm.sas_money.get_meter(isall=0)
                
                return True
            else:
                print("Failed to open SAS port")
                return False
        else:
            print("No SAS port found")
            return False

    def sas_polling_loop(self):
        """SAS polling loop - EXACT copy from production code"""
        if not self.running or not self.sas_comm or not self.sas_comm.is_port_open:
            return
        
        # Send poll
        self.sas_comm.send_general_poll()
        
        # Check for response
        time.sleep(0.05)  # Give time for response
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        # Schedule next poll - EXACT timing from production
        if self.running:
            self.sas_poll_timer = threading.Timer(0.04, self.sas_polling_loop)  # 40ms like working code
            self.sas_poll_timer.daemon = True
            self.sas_poll_timer.start()

    def test_sas_commands(self):
        """Test basic SAS commands - EXACT copy from production code"""
        if not self.sas_comm:
            print("SAS not initialized")
            return
            
        print("Testing SAS commands...")
        
        # Test SAS version
        print("Requesting SAS version...")
        self.sas_comm.request_sas_version()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        time.sleep(1)
        
        # Test balance query
        print("Requesting balance info...")
        self.sas_comm.request_balance_info()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)

    def test_aft_registration_and_transfer(self):
        """Test AFT registration and transfer with production-style polling active"""
        print("\n🧪 Testing AFT Registration and Transfer...")
        
        if not self.sas_comm:
            print("❌ SAS not initialized")
            return False
        
        try:
            # Get asset number
            asset_number = self.sas_comm.get_asset_number_for_aft()
            print(f"[AFT TEST] Using asset number: {asset_number}")
            
            # Get registration key from config - use the correct all-zeros key
            registration_key = self.config.get('SAS_MACHINE', 'registration_key', fallback='00000000000000000000000000000000000000000000')
            print(f"[AFT TEST] Using registration key: {registration_key}")
            
            # Step 1: AFT Registration
            print(f"[AFT TEST] Step 1: AFT Registration...")
            reg_result = self.sas_comm.sas_money.komut_aft_registration(
                asset_number, registration_key, "TEST01"
            )
            print(f"[AFT TEST] Registration result: {reg_result}")
            
            # Wait for registration to process with polling active
            print(f"[AFT TEST] Waiting for registration to process...")
            time.sleep(3)
            
            # Step 2: Test AFT lock first
            print(f"[AFT TEST] Step 2: Testing AFT lock...")
            lock_result = self.sas_comm.sas_money.komut_aft_lock_machine()
            print(f"[AFT TEST] Lock result: {lock_result}")
            
            time.sleep(2)  # Wait for lock to process
            
            # Step 3: Test transfer
            print(f"[AFT TEST] Step 3: Test transfer ($1.00)...")
            transfer_result = self.sas_comm.sas_money.komut_para_yukle(
                customerbalance=1.0,  # $1.00 in dollars
                customerpromo=0.0,
                transfertype=10,  # Cashable
                assetnumber=asset_number,
                registrationkey=registration_key
            )
            print(f"[AFT TEST] Transfer result: {transfer_result}")
            
            # Wait for transfer to process
            print(f"[AFT TEST] Waiting for transfer to process...")
            time.sleep(5)
            
            # Step 4: Check balance
            print(f"[AFT TEST] Step 4: Check balance...")
            balance_result = self.sas_comm.sas_money.komut_bakiye_sorgulama(
                "AFTTest", False, "ProductionTest"
            )
            print(f"[AFT TEST] Balance result: {balance_result}")
            
            # Step 5: Unlock machine
            print(f"[AFT TEST] Step 5: Unlocking machine...")
            unlock_result = self.sas_comm.sas_money.komut_aft_unlock_machine()
            print(f"[AFT TEST] Unlock result: {unlock_result}")
            
            # Analyze results
            if transfer_result:
                print(f"✅ AFT transfer completed with result: {transfer_result}")
                return True
            else:
                print(f"❌ AFT transfer failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during AFT test: {e}")
            return False

    def start(self):
        """Start the tester - EXACT pattern from production code"""
        print("🚀 Starting Production-Style AFT Tester...")
        
        if not self.initialize_sas():
            print("❌ Failed to initialize SAS. Exiting.")
            return False
        
        self.running = True
        
        # Test basic commands first
        self.test_sas_commands()
        
        # Start polling (CRITICAL!)
        print("✅ Starting SAS polling loop...")
        self.sas_polling_loop()
        
        # Wait for polling to stabilize
        print("⏳ Waiting for communication to stabilize...")
        time.sleep(3)
        
        # Now test AFT
        success = self.test_aft_registration_and_transfer()
        
        return success

    def shutdown(self):
        """Shutdown the tester - EXACT pattern from production code"""
        print("Shutting down...")
        self.running = False
        
        if self.sas_poll_timer:
            self.sas_poll_timer.cancel()
        
        if self.sas_comm:
            self.sas_comm.close_port()
        
        print("Shutdown complete.")

def main():
    print("🧪 Production-Style AFT Tester")
    print("This test follows the EXACT pattern used by the main application.")
    
    tester = ProductionStyleAFTTester()
    
    try:
        success = tester.start()
        
        if success:
            print("\n🎉 AFT TEST COMPLETED!")
            print("The test ran successfully with production-style polling.")
        else:
            print("\n❌ AFT TEST FAILED!")
            print("Check the logs above for details.")
        
        # Keep running for a bit to see any delayed responses
        print("\n⏳ Keeping polling active for 10 seconds to catch any delayed responses...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        tester.shutdown()

if __name__ == "__main__":
    main() 