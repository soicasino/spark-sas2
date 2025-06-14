#!/usr/bin/env python3
"""
Test script to try different machine unlock methods and AFT registration.
This script attempts various approaches to unlock the machine and enable AFT transfers.
"""

import asyncio
import time
from sas_communicator import SasCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager

async def test_machine_unlock():
    """Test different methods to unlock the machine and enable AFT"""
    
    print("=== Machine Unlock and AFT Test ===")
    
    # Initialize components
    config = ConfigManager()
    port = "/dev/ttyUSB1"  # Linux USB serial port
    print(f"Using port: {port}")
    
    # Create communicator
    communicator = SasCommunicator(config)
    money = SasMoney(config, communicator)
    
    try:
        # Open SAS port
        print("Opening SAS port...")
        if communicator.open_sas_port(port):
            print("✅ SAS port opened successfully")
        else:
            print("❌ Failed to open SAS port")
            return
        
        # Wait for initial communication
        await asyncio.sleep(2)
        
        print("\n=== Initial Balance Check ===")
        # Check initial balance
        balance_result = money.komut_bakiye_sorgulama("unlock_test", False, "initial_balance")
        balance_received = await money.wait_for_bakiye_sorgulama_completion(timeout=3)
        
        if balance_received:
            print("✅ Initial balance query successful")
        else:
            print("⚠️  Initial balance query failed")
        
        print(f"Balance received: {balance_received}")
        print(f"Current balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        print("\n=== Trying Different Unlock Methods ===")
        
        # Method 1: Standard unlock with asset number
        print("Method 1: Standard unlock with asset number")
        unlock_result = money.komut_unlock_machine()
        print(f"Unlock result: {unlock_result}")
        await asyncio.sleep(1)
        
        # Method 2: Unlock with zero asset number (sometimes needed for initial setup)
        print("Method 2: Unlock with zero asset number")
        unlock_result2 = money.komut_unlock_machine()  # This uses default asset number
        print(f"Unlock result: {unlock_result2}")
        await asyncio.sleep(1)
        
        # Method 3: AFT Registration
        print("Method 3: AFT Registration")
        try:
            # Use correct method name and provide required parameters
            asset_number = "0000006C"  # Known asset number (108 decimal)
            registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex key
            pos_id = "POS1"  # POS identifier
            
            reg_result = money.komut_aft_registration(asset_number, registration_key, pos_id)
            print(f"AFT Registration result: {reg_result}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"AFT Registration failed: {e}")
        
        # Method 4: Check AFT status after registration
        print("Method 4: Check AFT status")
        try:
            status_result = money.check_aft_status()
            print(f"AFT Status check result: {status_result}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"AFT Status check failed: {e}")
        
        print("\n=== Final Balance Check ===")
        # Check balance after unlock attempts
        balance_result2 = money.komut_bakiye_sorgulama("unlock_test", False, "post_unlock_balance")
        balance_received2 = await money.wait_for_bakiye_sorgulama_completion(timeout=3)
        
        if balance_received2:
            print("✅ Final balance query successful")
        else:
            print("⚠️  Final balance query failed")
        
        print(f"Final balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        # Method 5: Try a small test transfer if machine appears unlocked
        if money.yanit_bakiye_tutar > 0 or balance_received2:
            print("\n=== Test AFT Transfer ===")
            try:
                # Try a small $1.00 transfer
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
                transfer_success = await money.wait_for_para_yukle_completion(timeout=10)
                if transfer_success:
                    print("✅ Test transfer successful!")
                elif transfer_success is False:
                    print("❌ Test transfer failed")
                else:
                    print("⚠️  Test transfer timed out")
                    
            except Exception as e:
                print(f"Test transfer error: {e}")
        
    except Exception as e:
        print(f"Error in unlock test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nClosing SAS port...")
        communicator.close_sas_port()
        print("✅ Port closed")

if __name__ == "__main__":
    asyncio.run(test_machine_unlock()) 