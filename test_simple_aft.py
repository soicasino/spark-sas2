#!/usr/bin/env python3
"""
Simplified AFT test - skip complex registration, focus on transfer
"""

import time
import sys
import os
import threading

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from config_manager import ConfigManager

class AFTTester:
    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator = None
        self.money = None
        
    def start_polling(self):
        """Start background polling thread"""
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        print("Background polling started")
        
    def stop_polling(self):
        """Stop background polling"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1)
        print("Background polling stopped")
        
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

def test_simple_aft_transfer():
    """Test AFT transfer with proper polling"""
    
    print("=== Simple AFT Transfer Test with Polling ===")
    
    tester = AFTTester()
    
    # Initialize config and communicator
    config = ConfigManager()
    sas_port = config.get('sas', 'port', '/dev/ttyUSB1')
    
    print(f"Connecting to SAS port: {sas_port}")
    communicator = SASCommunicator(sas_port, config)
    
    if not communicator.open_port():
        print("Failed to open SAS port")
        return False
    
    # Initialize money functions
    from sas_money_functions import SasMoney
    money = SasMoney(config, communicator)
    
    # Set up tester
    tester.communicator = communicator
    tester.money = money
    
    print("SAS port opened successfully")
    
    try:
        # Start background polling
        tester.start_polling()
        
        # Known asset number from main app
        asset_number = "0000006C"  # 108 decimal
        registration_key = "00000000000000000000000000000000000000000000"  # All zeros
        
        print(f"Using asset number: {asset_number}")
        print(f"Using registration key: {registration_key}")
        
        # Wait for initial communication to stabilize
        print("Waiting for initial communication to stabilize...")
        time.sleep(2)
        
        # Test 1: Simple AFT status query
        print("\n--- Test 1: AFT Status Query ---")
        result = money.komut_bakiye_sorgulama("test", 0, "SimpleAFTTest")
        print(f"Balance query initiated, result: {result}")
        
        # Wait for response
        print("Waiting for balance response...")
        for i in range(10):  # Wait up to 5 seconds
            time.sleep(0.5)
            if not money.is_waiting_for_bakiye_sorgulama:
                print(f"Balance response received: {money.yanit_bakiye_tutar} TL")
                break
            print(f"Still waiting for balance response... ({i+1}/10)")
        
        # Test 2: Direct AFT transfer (no complex registration)
        print("\n--- Test 2: Direct AFT Transfer ---")
        print("Attempting 1 TL transfer without complex registration...")
        
        # Generate transaction ID
        transaction_id = int(time.time()) % 10000
        print(f"Using transaction ID: {transaction_id}")
        
        # Reset transfer status
        money.global_para_yukleme_transfer_status = None
        
        # Call money load function directly
        result = money.komut_para_yukle(
            doincreasetransactionid=0,
            transfertype=10,  # Cashable
            customerbalance=1.0,  # 1 TL
            customerpromo=0.0,
            transactionid=transaction_id,
            assetnumber=asset_number,
            registrationkey=registration_key
        )
        
        print(f"AFT transfer initiated, transaction ID: {result}")
        
        # Wait for responses and check status
        print("Waiting for AFT responses...")
        start_time = time.time()
        
        for i in range(20):  # Wait up to 10 seconds
            time.sleep(0.5)
            elapsed = time.time() - start_time
            
            # Check transfer status
            status = money.global_para_yukleme_transfer_status
            print(f"[{elapsed:.1f}s] Transfer status: {status}")
            
            if status == "00":
                print("✅ AFT Transfer SUCCESS!")
                break
            elif status in ["84", "87", "81"]:
                print(f"❌ AFT Transfer FAILED with status: {status}")
                break
            elif status == "40":
                print("⏳ AFT Transfer PENDING...")
            
        # Test 3: Check final balance
        print("\n--- Test 3: Final Balance Check ---")
        money.is_waiting_for_bakiye_sorgulama = True
        money.komut_bakiye_sorgulama("test", 0, "FinalBalanceCheck")
        
        # Wait for balance response
        for i in range(10):
            time.sleep(0.5)
            if not money.is_waiting_for_bakiye_sorgulama:
                break
            print(f"Waiting for final balance... ({i+1}/10)")
        
        print(f"Final balance: {money.yanit_bakiye_tutar} TL")
        
        # Test 4: Check for any final responses
        print("\n--- Test 4: Final Communication Check ---")
        for i in range(5):
            time.sleep(0.5)
            print(f"Final check {i+1}/5...")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        tester.stop_polling()
        communicator.close_port()
        print("SAS port closed")

if __name__ == "__main__":
    test_simple_aft_transfer() 