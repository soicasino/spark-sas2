#!/usr/bin/env python3
"""
Comprehensive AFT Test - Final Working Version

This script implements the EXACT logic from your working reference code:
1. Comprehensive AFT unlock sequence to resolve lock_status: FF, aft_status: B0
2. Continuous background polling to catch asynchronous responses
3. Proper AFT registration and transfer sequence
4. Exact command construction matching original working code
"""

import sys
import os
import time
import threading
import asyncio
from typing import Optional
from config_manager import ConfigManager
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

class ComprehensiveAFTTester:
    """Complete AFT test harness with all missing components"""

    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator: Optional[SASCommunicator] = None
        self.money: Optional[SasMoney] = None
        self.aft_future: Optional[asyncio.Future] = None
        self.config = None

    def _poll_loop(self):
        """
        Continuous background polling - equivalent to DoSASPoolingMsg from working code
        This is CRITICAL for catching AFT completion responses
        """
        print("[POLLING] Background polling started...")
        while self.running:
            try:
                if self.communicator and self.communicator.is_port_open:
                    # Get any data from SAS port
                    data = self.communicator.get_data_from_sas_port()
                    if data:
                        print(f"[POLLING] RX: {data}")
                        self.handle_response(data)
                        # Also let the communicator handle it
                        self.communicator.handle_received_sas_command(data)
                
                # Send general poll to keep communication alive
                if self.communicator:
                    self.communicator.send_general_poll()

                time.sleep(0.1)  # 100ms polling interval
                
            except Exception as e:
                print(f"[POLLING] Error: {e}")
                time.sleep(1)
                
        print("[POLLING] Stopped.")

    def handle_response(self, response: str):
        """Process responses and resolve Future on AFT completion"""
        if not response or not self.aft_future or self.aft_future.done():
            return

        try:
            # Handle AFT transfer responses (command 72h)
            if response.startswith("0172"):
                print(f"[HANDLER] AFT Response (72h) detected: {response}")
                if len(response) >= 10:
                    status_code = response[8:10]
                    print(f"[HANDLER] AFT Status Code: {status_code}")
                    
                    if status_code == "00":  # Success
                        print("[HANDLER] ✅ AFT Transfer SUCCESS!")
                        self.aft_future.set_result(True)
                    elif status_code == "40":  # Pending - continue waiting
                        print("[HANDLER] AFT Transfer pending, continuing to wait...")
                    else:  # Error
                        print(f"[HANDLER] ❌ AFT Transfer FAILED with status: {status_code}")
                        self.aft_future.set_exception(
                            Exception(f"AFT Failed with status: {status_code}")
                        )
                        
            # Handle AFT completion message (exception 69h)
            elif "69" in response:
                print(f"[HANDLER] AFT Completion (69h) detected: {response}")
                print("[HANDLER] ✅ AFT Transfer COMPLETED!")
                self.aft_future.set_result(True)
                
        except Exception as e:
            print(f"[HANDLER] Error processing response: {e}")

    def start(self):
        """Initialize components and start polling"""
        print("=== Comprehensive AFT Test - Final Version ===")
        print("Initializing SAS communication...")
        
        self.config = ConfigManager()
        
        # Get SAS port from config
        sas_port = self.config.get('sas', 'port', '/dev/ttyUSB1')
        print(f"Using SAS port: {sas_port}")
        
        # Initialize SAS communicator
        self.communicator = SASCommunicator(sas_port, self.config)
        if not self.communicator.open_port():
            raise ConnectionError(f"Failed to open SAS port {sas_port}. Check connection and ensure main app is not running.")
        
        # Initialize money functions
        self.money = SasMoney(self.config, self.communicator)
        print("✅ SAS communication initialized.")

        # Start background polling
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        print("✅ Background polling started.")

    def stop(self):
        """Stop polling and close port"""
        print("Stopping comprehensive AFT test...")
        self.running = False
        
        if self.poll_thread:
            self.poll_thread.join(timeout=2)
            
        if self.communicator:
            self.communicator.close_port()
            
        print("✅ Test stopped and port closed.")

    async def run_comprehensive_aft_test(self):
        """Execute the complete AFT test sequence with all fixes"""
        
        print("\n" + "="*60)
        print("STEP 1: COMPREHENSIVE AFT UNLOCK SEQUENCE")
        print("="*60)
        
        # This is the KEY missing piece - comprehensive AFT unlock
        print("[STEP 1] Performing comprehensive AFT unlock...")
        unlock_success = self.money.komut_comprehensive_aft_unlock()
        print(f"[STEP 1] Comprehensive AFT unlock result: {unlock_success}")
        
        # Wait for unlock to take effect
        await asyncio.sleep(2.0)
        
        print("\n" + "="*60)
        print("STEP 2: AFT REGISTRATION")
        print("="*60)
        
        # AFT Registration (required before transfers)
        asset_number = "0000006C"  # Your machine's asset number (108 decimal)
        registration_key = "0000000000000000000000000000000000000000"  # 40 chars
        pos_id = "POS1"
        
        print(f"[STEP 2] Starting AFT registration...")
        print(f"[STEP 2]   Asset Number: {asset_number}")
        print(f"[STEP 2]   Registration Key: {registration_key}")
        print(f"[STEP 2]   POS ID: {pos_id}")
        
        registration_success = self.money.komut_aft_registration(
            asset_number, registration_key, pos_id
        )
        print(f"[STEP 2] AFT registration result: {registration_success}")
        
        # Wait for registration to complete
        await asyncio.sleep(2.0)
        
        print("\n" + "="*60)
        print("STEP 3: AFT TRANSFER")
        print("="*60)
        
        # Set up Future for async waiting
        self.aft_future = asyncio.get_running_loop().create_future()
        
        # Perform AFT transfer using corrected method
        transfer_amount = 5.00  # $5.00 test transfer
        print(f"[STEP 3] Starting AFT transfer of ${transfer_amount}")
        
        try:
            # Call the corrected AFT transfer method
            transfer_result = self.money.komut_para_yukle(
                customerbalance=transfer_amount,
                assetnumber=asset_number,
                registrationkey=registration_key
            )
            print(f"[STEP 3] AFT transfer command sent: {transfer_result}")
            
        except Exception as e:
            print(f"[STEP 3] Error sending AFT transfer: {e}")
            return False
        
        print("\n" + "="*60)
        print("STEP 4: WAITING FOR AFT COMPLETION")
        print("="*60)
        
        print("[STEP 4] Waiting for AFT completion response...")
        print("[STEP 4] (Background polling will catch the response)")
        
        try:
            # Wait for AFT completion (with timeout)
            result = await asyncio.wait_for(self.aft_future, timeout=20.0)
            
            if result:
                print("\n" + "="*60)
                print("✅ AFT TRANSFER COMPLETED SUCCESSFULLY!")
                print("="*60)
                
                # Wait a moment then check final status
                await asyncio.sleep(1.0)
                
                # Query balance to see the result
                print("[FINAL] Querying final balance...")
                self.money.komut_bakiye_sorgulama("final_balance_check", False, "comprehensive_test_final")
                await asyncio.sleep(2.0)
                
                return True
            else:
                print("\n❌ AFT Transfer returned False")
                return False
                
        except asyncio.TimeoutError:
            print("\n" + "="*60)
            print("❌ AFT TRANSFER TIMED OUT")
            print("="*60)
            print("The transfer command was sent but no completion response received within 20 seconds.")
            return False
            
        except Exception as e:
            print(f"\n❌ AFT Transfer Failed: {e}")
            return False

async def main():
    """Main function to run the comprehensive test"""
    tester = ComprehensiveAFTTester()
    
    try:
        # Initialize and start
        tester.start()
        
        # Allow polling to stabilize
        await asyncio.sleep(1.0)
        
        # Run the comprehensive test
        success = await tester.run_comprehensive_aft_test()
        
        if success:
            print("\n🎉 COMPREHENSIVE AFT TEST PASSED!")
            print("The AFT system is working correctly with all fixes applied.")
        else:
            print("\n❌ COMPREHENSIVE AFT TEST FAILED")
            print("Check the logs above for specific error details.")
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always clean up
        tester.stop()
        print("\nTest completed.")

if __name__ == "__main__":
    print("Starting Comprehensive AFT Test...")
    asyncio.run(main()) 