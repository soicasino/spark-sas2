#!/usr/bin/env python3
"""
Debug script to test meter parsing with actual response data
"""

# Test data from the logs
test_data = "01AF880000A00009000000000089475290B800090000000000903522900200090000000000000000000300090000000000000000001E00090000000000000000000000090000000000131870000100090000000000129982000B0009000000000000276500A20009000000000000000000BA0009000000000000000000050004000103350600040000149840CD"

def analyze_meter_pattern(tdata):
    """Analyze the pattern in the meter data"""
    print("=== Pattern Analysis ===")
    
    # Skip header (01AF88)
    idx = 6
    data = tdata[idx:]
    
    print(f"Data: {data}")
    print(f"Length: {len(data)}")
    
    # Let's look for the repeating pattern
    # It seems like each meter follows: [padding?][meter_code][00][length][value]
    
    # Let's manually trace through the known good parsing:
    print("\nManual parsing trace:")
    
    positions = [
        (10, "A0", "894752.9"),  # Position 10-31
        (34, "B8", "903522.9"),  # Position 34-55  
        (58, "02", "0.0"),       # Position 58-79
        (82, "03", "0.0"),       # Position 82-103
        (106, "1E", "0.0"),      # Position 106-127
    ]
    
    for pos, code, value in positions:
        print(f"Position {pos}: code={code}, data around: {tdata[pos-2:pos+22]}")
    
    # Now let's see what's at position 130 where we stopped
    print(f"\nAt position 130 (where we stopped): {tdata[130:150]}")
    print(f"At position 134: {tdata[134:154]}")
    print(f"At position 138: {tdata[138:158]}")
    
    # Let's see if we can identify the next meter manually
    # From the output, we see "09000000000013187000" at position 134
    # This might be: 09 = length, followed by value 000000000013187000
    # But that doesn't match the pattern we've been following
    
    # Let's look at the structure differently
    # Maybe each meter is: [padding][code][padding][length][value]
    
    print("\nLooking for next valid meter after position 130:")
    for i in range(130, len(tdata), 2):
        if i + 2 <= len(tdata):
            code = tdata[i:i+2]
            known_codes = ['A0', 'B8', '02', '03', '1E', '01', '0B', 'A2', 'BA', '05', '06', '0C', '7F', 'FA', 'FB', 'FC', '1D', '04']
            if code in known_codes:
                print(f"Found meter code {code} at position {i}")
                print(f"Context: {tdata[i-4:i+20]}")
                break

def debug_af_parsing_v2(tdata):
    """Try a different approach to AF parsing"""
    print(f"=== AF Parsing V2 ===")
    
    # Skip header
    idx = 6
    message_length = (int(tdata[4:6], 16) * 2) + 10
    meter_data_end = message_length - 4
    
    parsed_meters = {}
    
    # Skip initial padding zeros
    while idx < meter_data_end and tdata[idx:idx+2] == "00":
        idx += 2
    
    print(f"Starting at index {idx} after skipping padding")
    
    known_codes = ['A0', 'B8', '02', '03', '1E', '01', '0B', 'A2', 'BA', '05', '06', '0C', '7F', 'FA', 'FB', 'FC', '1D', '04']
    
    while idx < meter_data_end:
        print(f"\nAt index {idx}: {tdata[idx:idx+10]}")
        
        # Look for next meter code
        found_meter = False
        for check_idx in range(idx, min(idx + 20, meter_data_end), 2):
            if check_idx + 2 <= meter_data_end:
                potential_code = tdata[check_idx:check_idx+2]
                if potential_code in known_codes:
                    print(f"Found meter code {potential_code} at {check_idx}")
                    idx = check_idx
                    found_meter = True
                    break
        
        if not found_meter:
            print("No more meter codes found")
            break
            
        meter_code = tdata[idx:idx+2]
        idx += 4  # Skip code + 00
        
        if idx + 2 > meter_data_end:
            break
            
        meter_length = int(tdata[idx:idx+2], 16)
        idx += 2
        hex_len = meter_length * 2
        
        if idx + hex_len > meter_data_end:
            break
            
        meter_val = tdata[idx:idx+hex_len]
        idx += hex_len
        
        print(f"  Code: {meter_code}, Length: {meter_length}, Value: {meter_val}")
        
        if meter_val:
            try:
                meter_value = int(meter_val) / 100.0
                parsed_meters[meter_code] = meter_value
                print(f"  Converted: {meter_value}")
            except:
                print(f"  Error converting {meter_val}")
    
    print(f"\nParsed meters: {parsed_meters}")

if __name__ == "__main__":
    analyze_meter_pattern(test_data)
    debug_af_parsing_v2(test_data) 