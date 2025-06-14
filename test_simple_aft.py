#!/usr/bin/env python3
"""
Simplified AFT test - skip complex registration, focus on transfer
"""

import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from config_manager import ConfigManager

def test_simple_aft_transfer():
    """Test AFT transfer without complex registration"""
    
    print("=== Simple AFT Transfer Test ===")
    
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
    
    print("SAS port opened successfully")
    
    try:
        # Known asset number from main app
        asset_number = "0000006C"  # 108 decimal
        registration_key = "00000000000000000000000000000000000000000000"  # All zeros
        
        print(f"Using asset number: {asset_number}")
        print(f"Using registration key: {registration_key}")
        
        # Test 1: Simple AFT status query
        print("\n--- Test 1: AFT Status Query ---")
        result = money.komut_bakiye_sorgulama("test", 0, "SimpleAFTTest")
        print(f"Balance query result: {result}")
        
        # Wait for response
        time.sleep(2)
        
        # Test 2: Direct AFT transfer (no complex registration)
        print("\n--- Test 2: Direct AFT Transfer ---")
        print("Attempting 1 TL transfer without complex registration...")
        
        # Generate transaction ID
        transaction_id = int(time.time()) % 10000
        print(f"Using transaction ID: {transaction_id}")
        
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
        money.komut_bakiye_sorgulama("test", 0, "FinalBalanceCheck")
        time.sleep(2)
        
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
        communicator.close_port()
        print("SAS port closed")

if __name__ == "__main__":
    test_simple_aft_transfer() 