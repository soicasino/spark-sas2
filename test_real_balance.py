#!/usr/bin/env python3
"""
Test real machine balance with proper communication
"""

import sys
import time
import asyncio
import configparser
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def test_real_balance():
    """Test real machine balance with proper communication"""
    print("=== Real Machine Balance Test ===")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Create communicator with specified port
    port = '/dev/ttyUSB1'
    print(f"Using port: {port}")
    comm = SASCommunicator(port, config)
    
    try:
        # Open the port
        print("Opening SAS port...")
        if not comm.open_port():
            print("ERROR: Could not open SAS port. Check connection and port name.")
            return
        
        print("✅ SAS port opened successfully")
        
        # Wait a moment for port to stabilize
        time.sleep(1)
        
        # Try to read asset number first
        print("\n=== Reading Asset Number ===")
        try:
            asset_num = comm.read_asset_number_from_machine()
            if asset_num:
                print(f"✅ Asset number read: {asset_num}")
                print(f"   Stored hex format: {getattr(comm, 'asset_number', 'Not set')}")
            else:
                print("⚠️  Could not read asset number, using default")
        except Exception as e:
            print(f"❌ Error reading asset number: {e}")
        
        # Check current balance values
        money = comm.sas_money
        print(f"\n=== Current Balance Values ===")
        print(f"Cashable: ${money.yanit_bakiye_tutar:.2f}")
        print(f"Restricted: ${money.yanit_restricted_amount:.2f}")
        print(f"Non-restricted: ${money.yanit_nonrestricted_amount:.2f}")
        
        # Send balance query
        print(f"\n=== Sending Balance Query ===")
        try:
            # Reset balance values to detect changes
            money.yanit_bakiye_tutar = -999  # Use sentinel value
            money.yanit_restricted_amount = -999
            money.yanit_nonrestricted_amount = -999
            
            print("Sending balance query command...")
            result = money.komut_bakiye_sorgulama("real_test", False, "real_balance_test")
            print(f"Command sent, result: {result}")
            
            # Wait for response with shorter timeout
            print("Waiting for balance response...")
            
            async def wait_for_balance():
                return await money.wait_for_bakiye_sorgulama_completion(timeout=3)
            
            balance_result = asyncio.run(wait_for_balance())
            print(f"Balance wait result: {balance_result}")
            
            # Check if values changed from sentinel
            if (money.yanit_bakiye_tutar != -999 or 
                money.yanit_restricted_amount != -999 or 
                money.yanit_nonrestricted_amount != -999):
                print("✅ Balance response received!")
                print(f"Final balance values:")
                print(f"  Cashable: ${money.yanit_bakiye_tutar:.2f}")
                print(f"  Restricted: ${money.yanit_restricted_amount:.2f}")
                print(f"  Non-restricted: ${money.yanit_nonrestricted_amount:.2f}")
                
                total = money.yanit_bakiye_tutar + money.yanit_restricted_amount + money.yanit_nonrestricted_amount
                print(f"  Total: ${total:.2f}")
                
                if total == 0:
                    print("ℹ️  Machine balance is $0.00 - this may be correct")
                else:
                    print(f"✅ Machine has balance: ${total:.2f}")
            else:
                print("❌ No balance response received - communication issue")
                
        except Exception as e:
            print(f"❌ Error in balance query: {e}")
            import traceback
            traceback.print_exc()
        
        # Test general polling to see if machine responds at all
        print(f"\n=== Testing General Communication ===")
        try:
            print("Sending general poll...")
            comm.send_general_poll()
            time.sleep(0.5)
            
            # Try to get any response
            response = comm.get_data_from_sas_port()
            if response:
                print(f"✅ Machine responded: {response}")
            else:
                print("❌ No response to general poll")
                
        except Exception as e:
            print(f"❌ Error in general communication test: {e}")
            
    finally:
        # Close the port
        print("\nClosing SAS port...")
        comm.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    test_real_balance() 