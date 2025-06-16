#!/usr/bin/env python3
"""
Test script to try different registration keys for AFT transfers.
This will help identify if the machine expects a specific registration key.
"""

import sys
import time
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from config_manager import ConfigManager

# Common registration keys used in slot machines
TEST_KEYS = [
    "00000000000000000000000000000000000000000000",  # All zeros (current)
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",  # All F's
    "1234567890ABCDEF1234567890ABCDEF12345678",  # Test pattern
    "0123456789ABCDEF0123456789ABCDEF01234567",  # Sequential pattern
    "ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD",  # ABCDEF pattern
    "1111111111111111111111111111111111111111",  # All 1's
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # All A's
    "0000000000000000000000000000000000000001",  # Almost all zeros with 1
    "DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF",  # DEADBEEF pattern
    "5555555555555555555555555555555555555555",  # All 5's
]

def test_registration_key(sas_comm, key, asset_number="0000006c"):
    """Test a specific registration key"""
    print(f"\n🔑 Testing registration key: {key}")
    
    try:
        # Step 1: Try AFT registration
        print(f"[REG] Attempting AFT registration...")
        reg_result = sas_comm.sas_money.komut_aft_registration(
            asset_number, key, "TEST01"
        )
        print(f"[REG] Registration result: {reg_result}")
        
        # Give time for registration to process
        time.sleep(1)
        
        # Step 2: Try a small test transfer
        print(f"[TRANSFER] Attempting small test transfer ($1)...")
        transfer_result = sas_comm.sas_money.komut_para_yukle(
            1,  # doincreasetransactionid
            "00",  # transfertype (cashable)
            100,  # customerbalance (cents)
            0,  # customerpromo
            "12345",  # transactionid
            asset_number,  # assetnumber
            key  # registrationkey
        )
        print(f"[TRANSFER] Transfer result: {transfer_result}")
        
        # Step 3: Check if transfer was successful
        if transfer_result and "success" in str(transfer_result).lower():
            print(f"✅ SUCCESS! Registration key {key} works!")
            return True
        elif transfer_result and "82" not in str(transfer_result):
            print(f"🟡 PARTIAL: Key {key} may work (no registration error)")
            return "partial"
        else:
            print(f"❌ FAILED: Key {key} rejected")
            return False
            
    except Exception as e:
        print(f"❌ Error testing key {key}: {e}")
        return False

def test_machine_specific_keys(sas_comm):
    """Try to derive machine-specific keys"""
    print(f"\n🔍 Attempting to derive machine-specific keys...")
    
    try:
        # Get machine serial number or ID if available
        asset_num = sas_comm.decimal_asset_number or 108
        
        # Generate keys based on asset number
        derived_keys = [
            f"{asset_num:040d}",  # Asset number padded to 40 digits
            f"{asset_num:08X}" + "0" * 32,  # Asset hex + zeros
            f"{asset_num:08X}" * 5,  # Asset hex repeated
        ]
        
        print(f"[DERIVED] Testing keys derived from asset number {asset_num}:")
        for key in derived_keys:
            print(f"[DERIVED] Testing: {key}")
            result = test_registration_key(sas_comm, key)
            if result is True:
                return key
                
    except Exception as e:
        print(f"❌ Error deriving machine keys: {e}")
    
    return None

def main():
    print("🔍 AFT Registration Key Tester")
    print("This script will test different registration keys to find one that works.")
    
    try:
        # Initialize config and communicator
        config = ConfigManager()
        sas_port = config.get('sas', 'port', '/dev/ttyUSB1')
        
        print(f"Connecting to SAS port: {sas_port}")
        sas_comm = SASCommunicator(sas_port, config)
        
        if not sas_comm.open_port():
            print("❌ Failed to initialize SAS communication")
            return
        
        print("✅ SAS communication initialized")
        
        # Get asset number
        asset_number = sas_comm.get_asset_number_for_aft()
        print(f"Using asset number: {asset_number}")
        
        working_keys = []
        partial_keys = []
        
        # Test all predefined keys
        print(f"\n🧪 Testing {len(TEST_KEYS)} predefined registration keys...")
        for i, key in enumerate(TEST_KEYS, 1):
            print(f"\n--- Test {i}/{len(TEST_KEYS)} ---")
            result = test_registration_key(sas_comm, key, asset_number)
            
            if result is True:
                working_keys.append(key)
                print(f"🎉 FOUND WORKING KEY: {key}")
                break  # Stop on first working key
            elif result == "partial":
                partial_keys.append(key)
            
            # Small delay between tests
            time.sleep(0.5)
        
        # If no working keys found, try machine-specific keys
        if not working_keys:
            print(f"\n🔍 No standard keys worked. Trying machine-specific keys...")
            derived_key = test_machine_specific_keys(sas_comm)
            if derived_key:
                working_keys.append(derived_key)
        
        # Summary
        print(f"\n📋 REGISTRATION KEY TEST SUMMARY:")
        print(f"Working keys: {len(working_keys)}")
        for key in working_keys:
            print(f"  ✅ {key}")
        
        print(f"Partial keys: {len(partial_keys)}")
        for key in partial_keys:
            print(f"  🟡 {key}")
        
        if working_keys:
            print(f"\n🎯 RECOMMENDATION:")
            print(f"Update your config.ini to use: {working_keys[0]}")
            print(f"This key should resolve the 'Registration key does not match' error.")
        elif partial_keys:
            print(f"\n🤔 PARTIAL SUCCESS:")
            print(f"Try these keys manually: {partial_keys}")
        else:
            print(f"\n❌ NO WORKING KEYS FOUND:")
            print(f"The machine may require a specific manufacturer key.")
            print(f"Contact the machine manufacturer or check documentation.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            sas_comm.close_port()
        except:
            pass

if __name__ == "__main__":
    main() 