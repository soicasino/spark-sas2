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

def read_asset_number_with_retry(communicator, max_attempts=10):
    """Read asset number with multiple attempts and proper response handling"""
    print(f"Reading asset number with up to {max_attempts} attempts...")
    
    for attempt in range(max_attempts):
        print(f"\n--- Attempt {attempt + 1} ---")
        
        # Send the asset number query command
        sas_address = communicator.sas_address
        command = f"{sas_address}7301FF"
        from utils import get_crc
        command_crc = get_crc(command)
        
        print(f"Sending asset number query: {command_crc}")
        communicator.sas_send_command_with_queue("ReadAssetNo", command_crc, 1)
        
        # Wait for response with longer timeout
        print("Waiting for response...")
        for check in range(50):  # Wait up to 10 seconds (50 * 0.2s)
            time.sleep(0.2)
            response = communicator.get_data_from_sas_port()
            if response:
                print(f"Response received: {response}")
                
                # Check if this is an asset number response (starts with 0173)
                if response.startswith('0173'):
                    print("Asset number response detected!")
                    
                    # Parse the asset number
                    if len(response) >= 16:
                        asset_hex = response[8:16]
                        print(f"Raw asset hex: {asset_hex}")
                        
                        if len(asset_hex) % 2 != 0:
                            asset_hex = '0' + asset_hex
                        
                        # Reverse by bytes (little-endian)
                        reversed_hex = ''.join([asset_hex[i:i+2] for i in range(len(asset_hex)-2, -2, -2)])
                        asset_dec = int(reversed_hex, 16)
                        
                        print(f"Asset number - HEX: {asset_hex}, Reversed: {reversed_hex}, DEC: {asset_dec}")
                        
                        # Store in communicator
                        communicator.asset_number = asset_hex
                        communicator.decimal_asset_number = asset_dec
                        
                        return asset_dec
                    else:
                        print("Asset number response too short")
                else:
                    print(f"Other response: {response}")
                    # Process other responses
                    communicator.handle_received_sas_command(response)
            else:
                if check % 10 == 0:  # Print every 2 seconds
                    print(f"Still waiting... ({check * 0.2:.1f}s)")
        
        print(f"Attempt {attempt + 1} failed - no asset number response")
        time.sleep(1)  # Wait 1 second before next attempt
    
    print(f"Failed to read asset number after {max_attempts} attempts")
    return None

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
    
    # Test 1: Read asset number with retry
    print("\n--- Test 1: Reading Asset Number (with retry) ---")
    asset_number = read_asset_number_with_retry(communicator, max_attempts=5)
    print(f"Final asset number result: {asset_number}")
    
    if asset_number is None:
        print("WARNING: Could not read asset number, using default")
        asset_number = 108  # Default value
    
    # Test 2: Send general polls to establish communication
    print("\n--- Test 2: Establishing Communication ---")
    print("Sending general polls...")
    for i in range(5):
        communicator.send_general_poll()
        time.sleep(0.5)
        
        # Check for any responses
        response = communicator.get_data_from_sas_port()
        if response:
            print(f"Poll response {i+1}: {response}")
            communicator.handle_received_sas_command(response)
        else:
            print(f"Poll {i+1}: No response")
    
    # Test 3: Full AFT registration
    print("\n--- Test 3: Full AFT Registration ---")
    try:
        asset_hex = f"{asset_number:08X}"
        registration_key = "00000000000000000000000000000000000000000000"
        pos_id = "POS001"
        
        print(f"Using asset number: {asset_hex}")
        print(f"Using registration key: {registration_key}")
        print(f"Using POS ID: {pos_id}")
        
        # Step 1: Initialize registration
        print("\nStep 1: Initialize AFT registration")
        sas_address = communicator.sas_address
        init_command = f"{sas_address}7301FF"
        from utils import get_crc
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
    
    # Cleanup
    print("\n--- Cleanup ---")
    communicator.close_port()
    print("Test completed")
    
    return True

if __name__ == "__main__":
    test_aft_registration() 