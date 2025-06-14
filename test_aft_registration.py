#!/usr/bin/env python3
"""
Test script to debug AFT registration process and responses
"""

import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from config_manager import ConfigManager

def test_aft_registration():
    """Test AFT registration process step by step"""
    
    print("=== AFT Registration Test ===")
    
    # Initialize config and communicator
    config = ConfigManager()
    sas_port = config.get('sas', 'port', '/dev/ttyUSB1')
    
    print(f"Connecting to SAS port: {sas_port}")
    communicator = SASCommunicator(sas_port, config)
    
    if not communicator.open_port():
        print("Failed to open SAS port")
        return False
    
    print("SAS port opened successfully")
    
    # Test 1: Read asset number
    print("\n--- Test 1: Reading Asset Number ---")
    asset_number = communicator.read_asset_number_from_machine()
    print(f"Asset number from machine: {asset_number}")
    
    # Test 2: Send AFT registration status query
    print("\n--- Test 2: AFT Registration Status Query ---")
    sas_address = communicator.sas_address
    command = f"{sas_address}7301FF"
    from utils import get_crc
    command_crc = get_crc(command)
    print(f"Sending AFT status query: {command_crc}")
    
    # Send command and wait for response
    communicator.sas_send_command_with_queue("AFTStatusQuery", command_crc, 1)
    
    # Wait and check for responses
    print("Waiting for responses...")
    for i in range(20):  # Wait up to 4 seconds
        time.sleep(0.2)
        response = communicator.get_data_from_sas_port()
        if response:
            print(f"Response {i+1}: {response}")
            # Process the response
            communicator.handle_received_sas_command(response)
        else:
            print(f"Check {i+1}: No response")
    
    # Test 3: Full AFT registration
    print("\n--- Test 3: Full AFT Registration ---")
    try:
        asset_hex = f"{asset_number:08X}" if asset_number else "0000006C"
        registration_key = "00000000000000000000000000000000000000000000"
        pos_id = "POS001"
        
        print(f"Using asset number: {asset_hex}")
        print(f"Using registration key: {registration_key}")
        print(f"Using POS ID: {pos_id}")
        
        result = communicator.sas_money.komut_aft_registration(asset_hex, registration_key, pos_id)
        print(f"AFT registration result: {result}")
        
        # Wait for registration responses
        print("Waiting for registration responses...")
        for i in range(30):  # Wait up to 6 seconds
            time.sleep(0.2)
            response = communicator.get_data_from_sas_port()
            if response:
                print(f"Registration response {i+1}: {response}")
                communicator.handle_received_sas_command(response)
            else:
                print(f"Registration check {i+1}: No response")
                
    except Exception as e:
        print(f"Error during AFT registration: {e}")
    
    # Test 4: Check AFT registration status
    print("\n--- Test 4: Check AFT Registration Status ---")
    if hasattr(communicator.sas_money, 'aft_registration_status'):
        print(f"AFT registration status: {communicator.sas_money.aft_registration_status}")
    else:
        print("AFT registration status not available")
    
    # Test 5: Try a simple AFT transfer
    print("\n--- Test 5: Simple AFT Transfer Test ---")
    try:
        # Reset transfer status
        communicator.sas_money.global_para_yukleme_transfer_status = None
        
        # Send a small test transfer
        transaction_id = communicator.sas_money.get_next_transaction_id()
        result = communicator.sas_money.komut_para_yukle(
            doincreasetransactionid=0,
            transfertype=10,  # Cashable
            customerbalance=1.0,  # 1 TL test
            customerpromo=0.0,
            transactionid=transaction_id,
            assetnumber=asset_hex,
            registrationkey=registration_key
        )
        
        print(f"AFT transfer command sent, transaction ID: {result}")
        
        # Wait for transfer response
        print("Waiting for transfer responses...")
        for i in range(40):  # Wait up to 8 seconds
            time.sleep(0.2)
            response = communicator.get_data_from_sas_port()
            if response:
                print(f"Transfer response {i+1}: {response}")
                communicator.handle_received_sas_command(response)
                
                # Check if we got a transfer status
                status = communicator.sas_money.global_para_yukleme_transfer_status
                if status:
                    print(f"Transfer status received: {status}")
                    break
            else:
                print(f"Transfer check {i+1}: No response")
        
        final_status = communicator.sas_money.global_para_yukleme_transfer_status
        print(f"Final transfer status: {final_status}")
        
    except Exception as e:
        print(f"Error during AFT transfer test: {e}")
    
    # Cleanup
    print("\n--- Cleanup ---")
    communicator.close_port()
    print("Test completed")
    
    return True

if __name__ == "__main__":
    test_aft_registration() 