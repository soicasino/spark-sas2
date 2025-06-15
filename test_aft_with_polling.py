#!/usr/bin/env python3
"""
Corrected AFT Test with Continuous Polling

This script demonstrates the correct way to test AFT by using a dedicated
background thread to continuously poll for SAS messages. This solves the
timing issue where asynchronous responses from the machine were being missed.
"""

import sys
import os
import time
import threading
import asyncio
from typing import Optional

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager
from utils import get_crc

class AFTTester:
    """A test harness that includes a vital background polling thread."""

    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator: Optional[SASCommunicator] = None
        self.money: Optional[SasMoney] = None
        self.aft_future: Optional[asyncio.Future] = None
        self.config = ConfigManager()

    def _poll_loop(self):
        """
        A dedicated background thread to continuously poll for SAS messages.
        This is critical for catching unsolicited responses like AFT completion.
        """
        print("[POLL_LOOP] Starting background polling...")
        while self.running:
            try:
                if self.communicator and hasattr(self.communicator, 'is_port_open') and self.communicator.is_port_open:
                    # Use the communicator's existing polling method
                    data = self.communicator.get_data_from_sas_port()
                    if data:
                        print(f"[POLL_LOOP] RX: {data}")
                        self.handle_response(data)
                
                # Send a general poll periodically to keep the connection alive
                if self.communicator:
                    self.communicator.send_general_poll()

                time.sleep(0.15)  # Poll every 150ms
            except Exception as e:
                print(f"[POLL_LOOP] Error: {e}")
                time.sleep(1)
        print("[POLL_LOOP] Stopped.")

    def handle_response(self, response: str):
        """
        Processes responses from the polling loop.
        If it's the AFT response we are waiting for, it resolves the Future.
        """
        if not response:
            return

        # Handle AFT transfer responses (command 72h)
        if response.startswith("0172"):
            print(f"[HANDLER] AFT Response (72h) detected: {response}")
            if self.aft_future and not self.aft_future.done():
                # Extract status code from position 8-10 in the response
                if len(response) >= 10:
                    status_code = response[8:10]
                    print(f"[HANDLER] AFT Status Code: {status_code}")
                    if status_code == "00":
                        print("[HANDLER] Success status detected. Resolving future.")
                        self.aft_future.set_result(True)
                    # Handle other statuses like "pending" (40) if needed
                    elif status_code == "40":
                        print("[HANDLER] Transfer pending, continuing to wait...")
                    elif status_code != "40":
                        self.aft_future.set_exception(
                            Exception(f"AFT Failed with status: {status_code}")
                        )
        
        # Handle AFT completion message (exception 69h)
        elif "01FF69" in response:
             print(f"[HANDLER] AFT Completion (69h) detected: {response}")
             if self.aft_future and not self.aft_future.done():
                print("[HANDLER] Success status detected from completion message. Resolving future.")
                self.aft_future.set_result(True)

    def start(self):
        """Initializes components and starts polling."""
        print("Initializing SAS communication...")
        
        # Initialize communicator with config - use the correct SAS port
        self.communicator = SASCommunicator('/dev/ttyUSB1', self.config)
        
        # Check if port is open
        if not hasattr(self.communicator, 'is_port_open') or not self.communicator.is_port_open:
            raise ConnectionError("Failed to open SAS port. Check connection and permissions.")
        
        self.money = SasMoney(self.config, self.communicator)
        print("✅ SAS communication initialized.")

        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def stop(self):
        """Stops polling and closes the port."""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1)
        if self.communicator and hasattr(self.communicator, 'close'):
            self.communicator.close()
        print("Polling stopped and port closed.")

    async def run_aft_test(self):
        """Executes the full AFT test sequence."""
        print("\n--- STEP 1: AFT Registration (Command 73h) ---")
        # In a real app, you'd get these from a secure source
        asset_number = "0000006C"
        registration_key = "0000000000000000000000000000000000000000"
        pos_id = "POS1"
        
        try:
            self.money.komut_aft_registration(asset_number, registration_key, pos_id)
            await asyncio.sleep(2)  # Wait for registration to process
        except Exception as e:
            print(f"Registration failed: {e}")
            return False

        print("\n--- STEP 2: AFT Transfer (Command 72h) ---")
        self.aft_future = asyncio.get_running_loop().create_future()
        
        # Call the corrected transfer function from sas_money_functions.py
        transaction_id = self.money.komut_para_yukle(
            doincreasetransactionid=1,
            transfertype=0,  # Cashable
            customerbalance=1.00,  # 1.00 TL
            customerpromo=0.0,
            transactionid=0,  # Let the function generate it
            assetnumber=asset_number,
            registrationkey=registration_key
        )
        print(f"Transfer command sent with transaction ID: {transaction_id}")
        
        print("\n--- STEP 3: Waiting for AFT completion response... ---")
        try:
            # Wait for the future to be resolved by the polling handler
            result = await asyncio.wait_for(self.aft_future, timeout=15.0)
            if result:
                print("\n--- ✅ AFT Transfer Succeeded! ---")
                
                # Check meters to see if coin-in updated
                print("\n--- STEP 4: Checking meters for coin-in update ---")
                await asyncio.sleep(1)  # Give machine time to update meters
                
                # Trigger meter query
                self.money.komut_get_meter(isall=0)
                await asyncio.sleep(3)  # Wait for meter response
                
                return True
        except asyncio.TimeoutError:
            print("\n--- ❌ AFT Transfer Timed Out. No response received. ---")
            return False
        except Exception as e:
            print(f"\n--- ❌ AFT Transfer Failed with error: {e} ---")
            return False

async def main():
    tester = AFTTester()
    try:
        tester.start()
        success = await tester.run_aft_test()
        
        if success:
            print("\n🎯 AFT TEST COMPLETED SUCCESSFULLY!")
            print("Now check if the coin-in meters have been updated.")
        else:
            print("\n❌ AFT TEST FAILED!")
            
    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
    finally:
        tester.stop()

if __name__ == "__main__":
    asyncio.run(main()) 