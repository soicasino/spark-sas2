#!/usr/bin/env python3

import sys
import configparser

# Clear any cached modules
modules_to_clear = [name for name in sys.modules.keys() if 'sas_money' in name]
for module in modules_to_clear:
    del sys.modules[module]

# Fresh import
from sas_money_functions import SasMoney

def test_meter_parsing():
    config = configparser.ConfigParser()
    config.read('config.ini')
    money = SasMoney(config, None)
    
    tdata = '012F380000A00089475290B80090352290020000000003000000001E00000000001318700001129982000B00276500A20000000000BA0000000000514C'
    
    print("Testing meter parsing with fresh import...")
    result = money.handle_single_meter_response(tdata)
    
    print("\n=== COMPARISON ===")
    print("Machine Screen Values:")
    print("  Total Bet (Coin In): 1,318,700.00 TL")
    print("  Total Won: 1,299,820.00 TL")
    
    print("\nParsed Values:")
    if result:
        for key, value in result.items():
            if 'turnover' in key or 'win' in key or 'coin' in key:
                print(f"  {key}: {value:,.2f} TL")
    
    # Manual test of the conversion
    print("\n=== MANUAL CONVERSION TEST ===")
    raw_val = "13187000"
    
    # Test decimal interpretation
    decimal_val = int(raw_val) / 100.0
    print(f"Raw: {raw_val} → Decimal: {decimal_val:,.2f}")
    
    # Test hex interpretation  
    hex_val = int(raw_val, 16) / 100.0
    print(f"Raw: {raw_val} → Hex: {hex_val:,.2f}")
    
    # Expected machine value
    print(f"Machine shows: 1,318,700.00")

if __name__ == "__main__":
    test_meter_parsing() 