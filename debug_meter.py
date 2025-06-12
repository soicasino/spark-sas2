#!/usr/bin/env python3
"""
Debug script to test meter parsing with actual response data
"""

# Test data from the logs
test_data = "01AF880000A00009000000000089475290B800090000000000903522900200090000000000000000000300090000000000000000001E00090000000000000000000000090000000000131870000100090000000000129982000B0009000000000000276500A20009000000000000000000BA0009000000000000000000050004000103350600040000149840CD"

def debug_af_parsing(tdata):
    """Debug AF meter parsing"""
    print(f"=== Debugging AF Meter Response ===")
    print(f"Raw data: {tdata}")
    print(f"Data length: {len(tdata)} chars")
    
    if len(tdata) < 10:
        print("Response too short")
        return
    
    idx = 0
    address = tdata[idx:idx+2]
    idx += 2
    command = tdata[idx:idx+2].upper()
    idx += 2
    length = tdata[idx:idx+2]
    idx += 2
    
    print(f"Address: {address}")
    print(f"Command: {command}")
    print(f"Length: {length} (decimal: {int(length, 16)})")
    
    message_length = (int(tdata[4:6], 16) * 2) + 10
    print(f"Expected message length: {message_length}")
    
    if command != "AF":
        print(f"Not an AF command: {command}")
        return
    
    # Calculate meter data end (exclude CRC)
    meter_data_end = message_length - 4
    print(f"Meter data ends at: {meter_data_end}")
    
    parsed_meters = {}
    try_count = 0
    
    print(f"\nStarting AF parsing at index {idx}")
    print(f"Remaining data: {tdata[idx:]}")
    
    # Let's also analyze the structure by looking for patterns
    print(f"\n=== Structure Analysis ===")
    remaining = tdata[idx:]
    print(f"Data from index {idx}: {remaining}")
    
    # Look for common meter codes in the data
    meter_codes = ['A0', 'B8', '02', '03', '1E', '01', '0B', 'A2', 'BA', '05', '06']
    for code in meter_codes:
        positions = []
        start = 0
        while True:
            pos = remaining.find(code, start)
            if pos == -1:
                break
            positions.append(pos + idx)
            start = pos + 1
        if positions:
            print(f"Meter code {code} found at positions: {positions}")
    
    while try_count < 15 and idx < meter_data_end:
        try_count += 1
        print(f"\n--- Try {try_count} ---")
        print(f"Current index: {idx}")
        
        # Get meter code
        if idx + 2 > meter_data_end:
            print("Not enough data for meter code")
            break
            
        meter_code = tdata[idx:idx+2].upper()
        print(f"Meter code at {idx}: {meter_code}")
        
        # Check if we have a valid meter code, skip padding zeros
        if meter_code == "00":
            print("Found padding zeros, skipping...")
            idx += 2
            continue
        
        # Check if this is a known meter code
        known_codes = ['A0', 'B8', '02', '03', '1E', '01', '0B', 'A2', 'BA', '05', '06', '0C', '7F', 'FA', 'FB', 'FC', '1D', '04']
        if meter_code not in known_codes:
            print(f"Unknown meter code {meter_code}, might be end of data")
            print(f"Next 20 chars: {tdata[idx:idx+20]}")
            break
            
        idx += 4  # Skip meter code + 00
        print(f"After skipping code+00, index: {idx}")
        
        # Get meter length
        if idx + 2 > meter_data_end:
            print("Not enough data for meter length")
            break
            
        meter_length_hex = tdata[idx:idx+2]
        meter_length = int(meter_length_hex, 16)
        idx += 2
        hex_len = meter_length * 2
        
        print(f"Meter length hex: {meter_length_hex}, decimal: {meter_length}, hex_len: {hex_len}")
        
        if meter_length == 0:
            print("Zero length meter, stopping")
            break
        
        # Get meter value
        if idx + hex_len > meter_data_end:
            print(f"Not enough data for meter value (need {hex_len}, have {meter_data_end - idx})")
            break
            
        meter_val = tdata[idx:idx+hex_len]
        idx += hex_len
        
        print(f"Meter value: {meter_val}")
        
        try:
            if meter_val:
                meter_value = int(meter_val) / 100.0
                print(f"Converted value: {meter_value}")
                parsed_meters[meter_code] = meter_value
            else:
                print("Empty meter value, skipping")
                
        except Exception as e:
            print(f"Error converting value: {e}")
            break
    
    print(f"\n=== Final Results ===")
    print(f"Parsed {len(parsed_meters)} meters:")
    for code, value in parsed_meters.items():
        print(f"  {code}: {value}")
    
    print(f"\nRemaining data after parsing: {tdata[idx:]}")

if __name__ == "__main__":
    debug_af_parsing(test_data) 