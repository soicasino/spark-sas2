#!/usr/bin/env python3
"""
Test machine unlock and AFT transfer functionality
"""

import sys
import time
import asyncio
import configparser
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def test_machine_unlock():
    """Test machine unlock and AFT functionality"""
    print("=== Machine Unlock and AFT Test ===")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Create communicator with correct port
    port = '/dev/ttyUSB1'
    print(f"Using port: {port}")
    comm = SASCommunicator(port, config)
    
    try:
        # Open the port
        print("Opening SAS port...")
        if not comm.open_port():
            print("ERROR: Could not open SAS port")
            return
        
        print("✅ SAS port opened successfully")
        
        # Wait a moment for initialization
        time.sleep(1)
        
        # Check initial balance
        print("\n=== Initial Balance Check ===")
        money = comm.sas_money
        result = money.komut_bakiye_sorgulama("unlock_test", False, "initial_balance")
        if result:
            print(f"✅ Initial balance query successful")
        else:
            print("⚠️  Initial balance query failed")
        
        # Wait for response
        balance_received = asyncio.run(money.wait_for_bakiye_sorgulama_completion(timeout=3))
        print(f"Balance received: {balance_received}")
        print(f"Current balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        # Machine status is shown in the balance response logs above
        
        # Try different unlock approaches
        print("\n=== Trying Different Unlock Methods ===")
        
        # Method 1: Standard unlock with asset number
        print("Method 1: Standard unlock with asset number")
        unlock_cmd = f"01740000006C{money.calculate_crc('01740000006C')}"
        print(f"Unlock command: {unlock_cmd}")
        result = comm.send_sas_command(unlock_cmd)
        print(f"Unlock result: {result}")
        time.sleep(1)
        
        # Method 2: Unlock with zero asset number
        print("Method 2: Unlock with zero asset number")
        unlock_cmd2 = f"017400000000{money.calculate_crc('017400000000')}"
        print(f"Unlock command: {unlock_cmd2}")
        result2 = comm.send_sas_command(unlock_cmd2)
        print(f"Unlock result: {result2}")
        time.sleep(1)
        
        # Method 3: AFT Registration to unlock
        print("Method 3: AFT Registration")
        reg_result = money.komut_aft_register("unlock_test")
        print(f"AFT Registration result: {reg_result}")
        time.sleep(2)
        
        # Check balance after unlock attempts
        print("\n=== Balance Check After Unlock ===")
        result = money.komut_bakiye_sorgulama("unlock_test", False, "post_unlock_balance")
        if result:
            print(f"✅ Post-unlock balance query successful")
        else:
            print("⚠️  Post-unlock balance query failed")
        
        # Wait for response
        balance_received = asyncio.run(money.wait_for_bakiye_sorgulama_completion(timeout=3))
        print(f"Balance received: {balance_received}")
        print(f"Updated balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        # Updated machine status is shown in the balance response logs above
        
        # Try a small AFT transfer
        print("\n=== Testing Small AFT Transfer ===")
        transfer_result = money.komut_para_yukle(
            doincreasetransactionid=1,
            transfertype=10,  # Cashable
            customerbalance=5.0,  # Small amount
            customerpromo=0.0,
            transactionid=9999,
            assetnumber="0000006c",
            registrationkey="00000000000000000000000000000000000000000000"
        )
        print(f"Transfer result: {transfer_result}")
        
        # Wait for transfer completion
        print("Waiting for transfer completion...")
        transfer_completed = asyncio.run(money.wait_for_para_yukle_completion(timeout=10))
        print(f"Transfer completed: {transfer_completed}")
        print(f"Transfer status: {money.get_transfer_status_description(money.transfer_status)}")
        
        # Final balance check
        print("\n=== Final Balance Check ===")
        result = money.komut_bakiye_sorgulama("unlock_test", False, "final_balance")
        if result:
            balance_received = asyncio.run(money.wait_for_bakiye_sorgulama_completion(timeout=3))
            print(f"Final balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
    except Exception as e:
        print(f"Error in unlock test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the port
        print("\nClosing SAS port...")
        comm.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    test_machine_unlock() 