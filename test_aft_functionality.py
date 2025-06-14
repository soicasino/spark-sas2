#!/usr/bin/env python3
"""
Simple AFT functionality test to verify transfers work despite lock status FF.
This focuses on testing the core AFT transfer functionality.
"""

import asyncio
import time
import threading
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager

class AFTTester:
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
        """Background polling loop to receive SAS responses"""
        while self.running:
            try:
                if self.communicator and self.communicator.is_port_open:
                    # Get any incoming data
                    data = self.communicator.get_data_from_sas_port()
                    if data:
                        print(f"RX: {data}")
                        # Process the received data
                        self.communicator.handle_received_sas_command(data)
                    
                    # Send periodic general poll (alternating 80/81)
                    self.communicator.send_general_poll()
                    
                time.sleep(0.1)  # Poll every 100ms
            except Exception as e:
                print(f"Error in polling loop: {e}")
                time.sleep(0.5)

async def test_aft_functionality():
    """Test AFT functionality despite lock status"""
    
    print("=== AFT Functionality Test ===")
    print("Testing if AFT transfers work despite machine lock status FF")
    
    tester = AFTTester()
    
    # Initialize components
    config = ConfigManager()
    port = "/dev/ttyUSB1"  # Linux USB serial port
    print(f"Using port: {port}")
    
    # Create communicator
    communicator = SASCommunicator(port, config)
    money = SasMoney(config, communicator)
    
    # Set up tester
    tester.communicator = communicator
    
    try:
        # Open SAS port
        print("Opening SAS port...")
        if communicator.open_port():
            print("✅ SAS port opened successfully")
        else:
            print("❌ Failed to open SAS port")
            return
        
        # Start background polling to receive responses
        tester.start_polling()
        
        # Wait for initial communication to stabilize
        print("Waiting for initial communication to stabilize...")
        await asyncio.sleep(3)
        
        # Step 1: AFT Registration
        print("\n=== Step 1: AFT Registration ===")
        asset_number = "0000006C"  # Known asset number
        registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex key
        pos_id = "POS1"  # POS identifier
        
        try:
            reg_result = money.komut_aft_registration(asset_number, registration_key, pos_id)
            print(f"AFT Registration result: {reg_result}")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"AFT Registration failed: {e}")
        
        # Step 2: Accept Lock Status FF (Test Mode)
        print("\n=== Step 2: Accept Machine State ===")
        balance_result = money.komut_bakiye_sorgulama("aft_test", False, "status_check")
        balance_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received:
            print("✅ Balance query successful")
            lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            print(f"🏭 Machine Lock Status: {lock_status}")
            print(f"🏭 AFT Status: {aft_status}")
            
            if lock_status == "FF":
                print("🔍 ANALYSIS: Machine in test/simulation mode (all locks reported)")
                print("💡 STRATEGY: Proceeding with AFT test despite lock status")
            else:
                print(f"🔍 ANALYSIS: Partial lock status: {lock_status}")
        else:
            print("⚠️  Balance query failed")
            return
        
        # Step 3: Test Small AFT Transfer
        print("\n=== Step 3: Test AFT Transfer (Simulation Mode) ===")
        try:
            # Try a small $1.00 transfer
            print("💰 Attempting $1.00 test transfer...")
            transfer_result = money.komut_para_yukle(
                doincreasetransactionid=True,
                transfertype=0,  # Non-restricted
                customerbalance=1.00,  # $1.00
                customerpromo=0.00,
                transactionid=0,
                assetnumber=asset_number,
                registrationkey=registration_key
            )
            print(f"Test transfer initiated: {transfer_result}")
            
            # Wait for transfer completion
            print("⏳ Waiting for transfer completion...")
            transfer_success = await money.wait_for_para_yukle_completion(timeout=15)
            
            if transfer_success is True:
                print("✅ TEST RESULT: AFT transfer successful!")
                print("🎯 CONCLUSION: Machine AFT functionality works despite lock status FF")
                
                # Check balance after transfer
                print("💰 Checking balance after transfer...")
                balance_result2 = money.komut_bakiye_sorgulama("aft_test", False, "post_transfer")
                balance_received2 = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
                
                if balance_received2:
                    print(f"New balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
                
            elif transfer_success is False:
                print("❌ TEST RESULT: AFT transfer failed")
                print("🔍 ANALYSIS: AFT may not be properly configured or machine has real restrictions")
            else:
                print("⏳ TEST RESULT: AFT transfer timed out")
                print("🔍 ANALYSIS: Machine may be processing or have timing issues")
                
        except Exception as e:
            print(f"Test transfer error: {e}")
        
        # Step 4: Final Status Check
        print("\n=== Step 4: Final Status Check ===")
        final_balance = money.komut_bakiye_sorgulama("aft_test", False, "final_check")
        final_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if final_received:
            final_lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            final_aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            
            print(f"📊 Final Machine Status:")
            print(f"   Lock Status: {final_lock_status}")
            print(f"   AFT Status: {final_aft_status}")
            print(f"   Balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
            
            if final_lock_status == "FF":
                print("🏭 CONCLUSION: Machine remains in test/simulation mode")
                print("💡 RECOMMENDATION: Use machine as-is for testing AFT functionality")
                print("⚠️  NOTE: Lock status FF may be normal for this test environment")
            
        # Give some time for any final responses
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Error in AFT test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nCleaning up...")
        tester.stop_polling()
        communicator.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    asyncio.run(test_aft_functionality()) 