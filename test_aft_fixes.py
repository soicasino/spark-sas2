#!/usr/bin/env python3
"""
Test script to verify AFT registration and lock command fixes.
This script tests the corrected AFT registration and lock commands.
"""

import sys
import time
import configparser
from port_manager import PortManager
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def test_aft_fixes():
    """Test the fixed AFT registration and lock commands"""
    print("🧪 Testing AFT Registration and Lock Command Fixes")
    print("=" * 60)
    
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Initialize port manager and find SAS port
    port_manager = PortManager(config)
    sas_port, device_type = port_manager.find_sas_port()
    
    if not sas_port:
        print("❌ No SAS port found!")
        return False
    
    print(f"✅ Using SAS port: {sas_port}, device type: {device_type}")
    
    # Initialize SAS communicator
    communicator = SASCommunicator(config, sas_port, device_type)
    
    # Read asset number
    asset_number_dec = communicator.read_asset_number_from_machine()
    if not asset_number_dec:
        print("❌ Could not read asset number!")
        return False
    
    asset_number_hex = f"{asset_number_dec:08x}"
    print(f"✅ Asset number: {asset_number_dec} (hex: {asset_number_hex})")
    
    # Initialize SAS money functions
    sas_money = SasMoney(config, communicator)
    
    # Start polling to keep machine responsive
    print("🔄 Starting background polling...")
    communicator.start_polling()
    time.sleep(2)
    
    try:
        # Test 1: AFT Registration with fixed command format
        print("\n" + "─" * 60)
        print("🧪 TEST 1: AFT Registration (Fixed Format)")
        print("─" * 60)
        
        registration_key = config.get('sas', 'registrationkey', '0' * 40)
        pos_id = "TEST01"
        
        print(f"Using registration key: {registration_key}")
        print(f"Using POS ID: {pos_id}")
        
        # Perform AFT registration
        registration_result = sas_money.komut_aft_registration(
            asset_number_hex, 
            registration_key, 
            pos_id
        )
        
        print(f"Registration result: {registration_result}")
        
        # Wait for registration to complete
        time.sleep(3)
        
        # Test 2: Check AFT status after registration
        print("\n" + "─" * 60)
        print("🧪 TEST 2: Check AFT Status After Registration")
        print("─" * 60)
        
        sas_money.komut_bakiye_sorgulama("test_registration", False, "test_after_registration")
        time.sleep(2)
        
        if hasattr(communicator, 'last_aft_status'):
            aft_status = communicator.last_aft_status
            lock_status = communicator.last_game_lock_status
            print(f"AFT Status: {aft_status}")
            print(f"Lock Status: {lock_status}")
            
            if aft_status in ['01', '80']:  # Registered or ready
                print("✅ AFT registration appears successful!")
            else:
                print(f"⚠️  AFT status: {aft_status} - may need investigation")
        
        # Test 3: AFT Lock with fixed command format
        print("\n" + "─" * 60)
        print("🧪 TEST 3: AFT Lock (Fixed Format)")
        print("─" * 60)
        
        lock_result = sas_money.komut_aft_lock_machine(timeout_seconds=30)
        print(f"Lock result: {lock_result}")
        
        # Wait for lock to be processed
        time.sleep(3)
        
        # Check lock status
        sas_money.komut_bakiye_sorgulama("test_lock", False, "test_after_lock")
        time.sleep(2)
        
        if hasattr(communicator, 'last_game_lock_status'):
            lock_status = communicator.last_game_lock_status
            print(f"Lock Status after lock command: {lock_status}")
            
            if lock_status == '00':
                print("✅ Machine locked successfully!")
            elif lock_status == '40':
                print("⏳ Lock pending - this is normal")
            else:
                print(f"⚠️  Lock status: {lock_status} - may need investigation")
        
        # Test 4: AFT Unlock
        print("\n" + "─" * 60)
        print("🧪 TEST 4: AFT Unlock (Fixed Format)")
        print("─" * 60)
        
        unlock_result = sas_money.komut_aft_unlock_machine()
        print(f"Unlock result: {unlock_result}")
        
        # Wait for unlock to be processed
        time.sleep(3)
        
        # Check final status
        sas_money.komut_bakiye_sorgulama("test_unlock", False, "test_after_unlock")
        time.sleep(2)
        
        if hasattr(communicator, 'last_game_lock_status'):
            lock_status = communicator.last_game_lock_status
            print(f"Lock Status after unlock command: {lock_status}")
            
            if lock_status == 'FF':
                print("✅ Machine unlocked successfully!")
            else:
                print(f"⚠️  Lock status: {lock_status} - may still be locked")
        
        print("\n" + "=" * 60)
        print("🎯 AFT FIXES TEST COMPLETED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        # Stop polling and close port
        communicator.stop_polling()
        communicator.close_port()

if __name__ == "__main__":
    try:
        success = test_aft_fixes()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 