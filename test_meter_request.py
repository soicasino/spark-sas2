#!/usr/bin/env python3
"""
Test script to verify the updated meter request command
"""

def decode_af_command(command_hex):
    """Decode AF meter request command to show which meters are being requested"""
    print(f"=== Decoding AF Command: {command_hex} ===")
    
    if len(command_hex) < 6:
        print("Command too short")
        return
        
    idx = 0
    address = command_hex[idx:idx+2]
    idx += 2
    command = command_hex[idx:idx+2] 
    idx += 2
    length = command_hex[idx:idx+2]
    idx += 2
    
    print(f"Address: {address}")
    print(f"Command: {command}")
    print(f"Length: {length} (decimal: {int(length, 16)})")
    
    # Parse meter codes - each meter code is 2 bytes, no padding
    meter_data = command_hex[idx:-4]  # Exclude CRC
    print(f"Meter data: {meter_data}")
    
    print("Requested meters:")
    i = 0
    while i < len(meter_data):
        if i + 2 <= len(meter_data):
            meter_code = meter_data[i:i+2]
            print(f"  - Meter {meter_code}")
            i += 2
        else:
            break

# Test the original and new commands
print("ORIGINAL COMMAND:")
decode_af_command("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600")

print("\nNEW COMMAND:")
decode_af_command("01AF1E000000A000B800020003001E00000001000B00A200BA00050006000C00") 