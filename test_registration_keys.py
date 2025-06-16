#!/usr/bin/env python3
"""
Test script to try different registration keys for AFT transfers.
This will help identify if the machine expects a specific registration key.
"""

import sys
import time
from sas_communicator import SASCommunicator

# Common registration keys used in slot machines
TEST_KEYS = [
    "00000000000000000000000000000000000000000000",  # All zeros (current)
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",  # All F's
    "1234567890ABCDEF1234567890ABCDEF12345678",  # Test pattern
    "0123456789ABCDEF0123456789ABCDEF01234567",  # Sequential pattern
    "ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD",  # ABCDEF pattern
    "1111111111111111111111111111111111111111",  # All 1's
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # All A's
    "0000000000000000000000000000000000000001",  # Almost zeros with 1
]

def test_registration_key(sas_comm, key, asset_number):
    """Test a specific registration key"""
    print(f"\n{'='*60}")
    print(f"🔑 Testing Registration Key: {key}")
    print(f"{'='*60}")
    
    try:
        # Try AFT registration with this key
        print(f"[TEST] Attempting AFT registration...")
        result = sas_comm.sas_money.komut_aft_registration(
            asset_number, key, "TEST01"
        )
        print(f"[TEST] Registration result: {result}")
        
        if result:
            print(f"✅ Registration successful with key: {key}")
            
            # Try a small test transfer
            print(f"[TEST] Attempting small test transfer ($1.00)...")
            transfer_result = sas_comm.sas_money.komut_para_yukle(
                asset_number, 100, 0, key  # $1.00 transfer
            )
            print(f"[TEST] Transfer result: {transfer_result}")
            
            if transfer_result and transfer_result.get('success'):
                print(f"🎉 SUCCESS! Working registration key found: {key}")
                return key
            else:
                print(f"❌ Registration worked but transfer failed")
        else:
            print(f"❌ Registration failed with key: {key}")
            
    except Exception as e:
        print(f"❌ Error testing key {key}: {e}")
    
    return None

def main():
    print("🔍 AFT Registration Key Tester")
    print("This script will test different registration keys to find one that works.")
    
    # Initialize SAS communication
    try:
        sas_comm = SASCommunicator()
        if not sas_comm.initialize():
            print("❌ Failed to initialize SAS communication")
            return
        
        # Get asset number
        asset_number = "0000006c"  # From your logs
        print(f"📍 Using asset number: {asset_number}")
        
        # Test each registration key
        working_key = None
        for i, key in enumerate(TEST_KEYS, 1):
            print(f"\n🧪 Test {i}/{len(TEST_KEYS)}")
            working_key = test_registration_key(sas_comm, key, asset_number)
            
            if working_key:
                break
                
            # Small delay between tests
            time.sleep(2)
        
        if working_key:
            print(f"\n🎉 SOLUTION FOUND!")
            print(f"Working registration key: {working_key}")
            print(f"\nTo fix your application:")
            print(f"1. Update config.ini with: registration_key = {working_key}")
            print(f"2. Update routers/money_transfer.py with the same key")
            print(f"3. Restart your application")
        else:
            print(f"\n❌ No working registration key found.")
            print(f"This suggests the machine may have AFT disabled or")
            print(f"requires a specific manufacturer key.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            sas_comm.close()
        except:
            pass

if __name__ == "__main__":
    main() 