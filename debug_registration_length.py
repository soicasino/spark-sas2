#!/usr/bin/env python3
"""
Debug script to verify AFT registration command length calculation
"""

def debug_registration_command():
    """Debug the AFT registration command construction"""
    
    # Test data
    sas_address = "01"
    assetnumber = "0000006C"
    registrationkey = "00000000000000000000000000000000000000000000"
    posid = "POS001"
    
    # Convert POS ID to hex (pad to 8 characters)
    posid_hex = ''.join(f"{ord(c):02x}" for c in posid.ljust(4, '\x00')[:4])
    print(f"POS ID: '{posid}' -> hex: '{posid_hex}'")
    
    # Construct command data
    command_data = f"01{assetnumber}{registrationkey}{posid_hex}"
    print(f"Command data: {command_data}")
    print(f"Command data length (chars): {len(command_data)}")
    print(f"Command data length (bytes): {len(command_data) // 2}")
    
    # Calculate length
    data_length = len(command_data) // 2
    print(f"Calculated length: {data_length} (decimal) = {data_length:02X} (hex)")
    
    # Construct full command
    command = f"{sas_address}73{data_length:02X}{command_data}"
    print(f"Full command: {command}")
    
    # Break down the command
    print(f"\nCommand breakdown:")
    print(f"  SAS Address: {command[0:2]}")
    print(f"  Command: {command[2:4]}")
    print(f"  Length: {command[4:6]} ({int(command[4:6], 16)} decimal)")
    print(f"  Data: {command[6:]}")
    
    # Verify data components
    data_part = command[6:]
    print(f"\nData breakdown:")
    print(f"  Code: {data_part[0:2]}")
    print(f"  Asset Number: {data_part[2:10]}")
    print(f"  Registration Key: {data_part[10:50]}")
    print(f"  POS ID: {data_part[50:58]}")
    
    return command

if __name__ == "__main__":
    print("=== AFT Registration Command Length Debug ===")
    command = debug_registration_command()
    print(f"\nFinal command: {command}") 