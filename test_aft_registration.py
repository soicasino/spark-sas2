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
    
    # Use known asset number from main app logs
    print("\n--- Using Known Asset Number ---")
    asset_number = 108  # From main app logs
    asset_hex = f"{asset_number:08X}"  # 0000006C
    print(f"Using known asset number: {asset_number} (hex: {asset_hex})")
    
    # Store in communicator
    communicator.asset_number = asset_hex
    communicator.decimal_asset_number = asset_number
    
    # Test 1: Send general polls to establish communication
    print("\n--- Test 1: Establishing Communication ---")
    print("Sending general polls...")
    for i in range(3):
        communicator.send_general_poll()
        time.sleep(0.3)
        
        # Check for any responses
        response = communicator.get_data_from_sas_port()
        if response:
            print(f"Poll response {i+1}: {response}")
            communicator.handle_received_sas_command(response)
        else:
            print(f"Poll {i+1}: No response")
    
    # Test 2: AFT Registration Status Query
    print("\n--- Test 2: AFT Registration Status Query ---")
    sas_address = communicator.sas_address
    command = f"{sas_address}7301FF"
    from utils import get_crc
    command_crc = get_crc(command)
    print(f"Sending AFT status query: {command_crc}")
    
    communicator.sas_send_command_with_queue("AFTStatusQuery", command_crc, 1)
    
    # Wait for status response
    print("Waiting for AFT status response...")
    status_response_received = False
    for i in range(25):  # Wait up to 5 seconds
        time.sleep(0.2)
        response = communicator.get_data_from_sas_port()
        if response:
            print(f"Status response {i+1}: {response}")
            communicator.handle_received_sas_command(response)
            if response.startswith('0173'):
                status_response_received = True
                print("AFT status response received!")
                break
        else:
            if i % 5 == 0:
                print(f"Status waiting... ({i * 0.2:.1f}s)")
    
    if not status_response_received:
        print("WARNING: No AFT status response received")
    
    # Test 3: Full AFT registration
    print("\n--- Test 3: Full AFT Registration ---")
    try:
        registration_key = "00000000000000000000000000000000000000000000"
        pos_id = "POS001"
        
        print(f"Using asset number: {asset_hex}")
        print(f"Using registration key: {registration_key}")
        print(f"Using POS ID: {pos_id}")
        
        # Step 1: Initialize registration
        print("\nStep 1: Initialize AFT registration")
        init_command = f"{sas_address}7301FF"
        init_command_crc = get_crc(init_command)
        print(f"Sending init command: {init_command_crc}")
        
        communicator.sas_send_command_with_queue("AFTRegInit", init_command_crc, 1)
        
        # Wait for init response
        print("Waiting for init response...")
        init_response_received = False
        for i in range(25):  # Wait up to 5 seconds
            time.sleep(0.2)
            response = communicator.get_data_from_sas_port()
            if response:
                print(f"Init response {i+1}: {response}")
                communicator.handle_received_sas_command(response)
                if response.startswith('0173'):
                    init_response_received = True
                    print("Init response received!")
                    break
            else:
                if i % 5 == 0:
                    print(f"Init waiting... ({i * 0.2:.1f}s)")
        
        if not init_response_received:
            print("WARNING: No init response received")
        
        # Step 2: Complete registration
        print("\nStep 2: Complete AFT registration")
        time.sleep(1)  # Wait a moment
        
        # Convert POS ID to hex
        posid_hex = ''.join(f"{ord(c):02x}" for c in pos_id.ljust(4, '\x00')[:4])
        print(f"POS ID hex: {posid_hex}")
        
        # Construct complete registration command
        command_data = f"01{asset_hex}{registration_key}{posid_hex}"
        command = f"{sas_address}73{len(command_data)//2:02X}{command_data}"
        command_crc = get_crc(command)
        
        print(f"Complete registration command: {command_crc}")
        communicator.sas_send_command_with_queue("AFTRegComplete", command_crc, 1)
        
        # Wait for complete response
        print("Waiting for complete registration response...")
        complete_response_received = False
        for i in range(25):  # Wait up to 5 seconds
            time.sleep(0.2)
            response = communicator.get_data_from_sas_port()
            if response:
                print(f"Complete response {i+1}: {response}")
                communicator.handle_received_sas_command(response)
                if response.startswith('0173'):
                    complete_response_received = True
                    print("Complete registration response received!")
                    break
            else:
                if i % 5 == 0:
                    print(f"Complete waiting... ({i * 0.2:.1f}s)")
        
        if not complete_response_received:
            print("WARNING: No complete registration response received")
                
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
        print(f"Using transaction ID: {transaction_id}")
        
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
        transfer_response_received = False
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
                    transfer_response_received = True
                    break
                    
                # Also check for AFT responses (0172)
                if response.startswith('0172'):
                    print("AFT transfer response detected!")
                    transfer_response_received = True
            else:
                if i % 10 == 0:
                    print(f"Transfer waiting... ({i * 0.2:.1f}s)")
        
        final_status = communicator.sas_money.global_para_yukleme_transfer_status
        print(f"Final transfer status: {final_status}")
        
        if not transfer_response_received:
            print("WARNING: No transfer response received")
        
    except Exception as e:
        print(f"Error during AFT transfer test: {e}")
    
    # Test 6: Send some general polls to see what happens
    print("\n--- Test 6: Final Communication Check ---")
    print("Sending final polls...")
    for i in range(5):
        communicator.send_general_poll()
        time.sleep(0.3)
        
        # Check for any responses
        response = communicator.get_data_from_sas_port()
        if response:
            print(f"Final poll response {i+1}: {response}")
            communicator.handle_received_sas_command(response)
        else:
            print(f"Final poll {i+1}: No response")
    
    # Cleanup
    print("\n--- Cleanup ---")
    communicator.close_port()
    print("Test completed")
    
    return True

if __name__ == "__main__":
    test_aft_registration() 