#!/usr/bin/env python3
"""
Test script to debug balance query issues
"""

import sys
import time
import asyncio
import configparser
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def test_balance_query():
    """Test balance query functionality"""
    print("=== Balance Query Test ===")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Create communicator
    comm = SASCommunicator('COM3', config)
    
    print(f"SAS Address: {comm.sas_address}")
    print(f"Device Type ID: {comm.device_type_id}")
    
    # Check asset number storage
    print(f"Asset number (hex): {getattr(comm, 'asset_number', 'Not set')}")
    print(f"Asset number (decimal): {getattr(comm, 'decimal_asset_number', 'Not set')}")
    
    # Check current balance values
    money = comm.sas_money
    print(f"Current balance values:")
    print(f"  Cashable: {money.yanit_bakiye_tutar}")
    print(f"  Restricted: {money.yanit_restricted_amount}")
    print(f"  Non-restricted: {money.yanit_nonrestricted_amount}")
    
    # Test asset number reading
    print("\n=== Testing Asset Number Reading ===")
    try:
        asset_num = comm.read_asset_number_from_machine()
        print(f"Asset number read: {asset_num}")
        print(f"Stored asset number (hex): {getattr(comm, 'asset_number', 'Not set')}")
        print(f"Stored asset number (decimal): {getattr(comm, 'decimal_asset_number', 'Not set')}")
    except Exception as e:
        print(f"Error reading asset number: {e}")
    
    # Test balance query command construction
    print("\n=== Testing Balance Query Command ===")
    try:
        # Check what asset number will be used
        asset_number = "0000006C"  # Default
        if hasattr(comm, 'asset_number') and comm.asset_number:
            asset_number = comm.asset_number.upper()
        elif hasattr(comm, 'asset_number_hex') and comm.asset_number_hex:
            asset_number = comm.asset_number_hex.upper()
        
        print(f"Asset number for balance query: {asset_number}")
        
        # Construct the command manually to see what it looks like
        sas_address = comm.sas_address
        command = f"{sas_address}74{asset_number}"
        from utils import get_crc
        command_with_crc = get_crc(command)
        
        print(f"Balance query command: {command_with_crc}")
        
        # Test the actual balance query
        print("\n=== Sending Balance Query ===")
        result = money.komut_bakiye_sorgulama("test", False, "balance_test")
        print(f"Balance query result: {result}")
        
        # Wait for response
        print("Waiting for balance response...")
        async def wait_for_balance():
            return await money.wait_for_bakiye_sorgulama_completion(timeout=10)
        
        balance_result = asyncio.run(wait_for_balance())
        print(f"Balance wait result: {balance_result}")
        
        # Check final balance values
        print(f"Final balance values:")
        print(f"  Cashable: {money.yanit_bakiye_tutar}")
        print(f"  Restricted: {money.yanit_restricted_amount}")
        print(f"  Non-restricted: {money.yanit_nonrestricted_amount}")
        
    except Exception as e:
        print(f"Error in balance query test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_balance_query() 