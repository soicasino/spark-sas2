#!/usr/bin/env python3
"""
Test balance response parsing with simulated data
"""

import sys
import configparser
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def test_balance_parsing():
    """Test balance response parsing with known data"""
    print("=== Balance Response Parsing Test ===")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Create communicator (no need to open port for parsing test)
    comm = SASCommunicator('COM3', config)
    money = comm.sas_money
    
    # Test BCD conversion function
    print("\n=== Testing BCD Conversion ===")
    test_bcd_values = [
        ("0000000000", 0),      # Zero
        ("0000002000", 2000),   # $20.00 in cents
        ("0000005000", 5000),   # $50.00 in cents
        ("0000010000", 10000),  # $100.00 in cents
        ("0000001000", 1000),   # $10.00 in cents
    ]
    
    for bcd_str, expected in test_bcd_values:
        try:
            result = money.bcd_to_int(bcd_str)
            dollars = result / 100
            print(f"BCD: {bcd_str} -> {result} cents -> ${dollars:.2f} (expected: ${expected/100:.2f})")
            if result != expected:
                print(f"  ERROR: Expected {expected}, got {result}")
        except Exception as e:
            print(f"  ERROR converting {bcd_str}: {e}")
    
    # Test with a simulated balance response
    print("\n=== Testing Balance Response Parsing ===")
    
    # Simulate a balance response with $20.00 cashable balance
    # Format: Address(01) + Command(74) + Length(1E) + AssetNumber(0000006C) + 
    #         GameLockStatus(00) + AvailableTransfers(FF) + HostCashoutStatus(00) + 
    #         AFTStatus(B0) + MaxBufferIndex(00) + 
    #         CashableAmount(0000002000) + RestrictedAmount(0000000000) + NonRestrictedAmount(0000000000)
    simulated_response = "01741E0000006C00FF00B0000000002000000000000000000000000000"
    
    print(f"Simulated response: {simulated_response}")
    print(f"Response length: {len(simulated_response)} characters")
    
    # Reset balance values
    money.yanit_bakiye_tutar = 0
    money.yanit_restricted_amount = 0
    money.yanit_nonrestricted_amount = 0
    
    # Parse the simulated response
    try:
        money.yanit_bakiye_sorgulama(simulated_response)
        
        print(f"Parsed balance values:")
        print(f"  Cashable: ${money.yanit_bakiye_tutar:.2f}")
        print(f"  Restricted: ${money.yanit_restricted_amount:.2f}")
        print(f"  Non-restricted: ${money.yanit_nonrestricted_amount:.2f}")
        
        if money.yanit_bakiye_tutar == 20.0:
            print("✅ Balance parsing working correctly!")
        else:
            print(f"❌ Balance parsing issue: expected $20.00, got ${money.yanit_bakiye_tutar:.2f}")
            
    except Exception as e:
        print(f"Error parsing simulated response: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different balance amounts
    print("\n=== Testing Different Balance Amounts ===")
    test_cases = [
        ("01741E0000006C00FF00B0000000000000000000000000000000000000", 0, 0, 0),      # All zero
        ("01741E0000006C00FF00B0000000001000000000000000000000000000", 10, 0, 0),     # $10 cashable
        ("01741E0000006C00FF00B0000000000000000000050000000000000000", 0, 50, 0),     # $50 restricted
        ("01741E0000006C00FF00B0000000000000000000000000000000001500", 0, 0, 15),     # $15 non-restricted
        ("01741E0000006C00FF00B0000000002000000000100000000000000500", 20, 10, 5),   # Mixed amounts
    ]
    
    for response, exp_cash, exp_rest, exp_nonrest in test_cases:
        money.yanit_bakiye_tutar = 0
        money.yanit_restricted_amount = 0
        money.yanit_nonrestricted_amount = 0
        
        try:
            money.yanit_bakiye_sorgulama(response)
            print(f"Response: {response[:20]}...")
            print(f"  Expected: C=${exp_cash:.2f}, R=${exp_rest:.2f}, N=${exp_nonrest:.2f}")
            print(f"  Got:      C=${money.yanit_bakiye_tutar:.2f}, R=${money.yanit_restricted_amount:.2f}, N=${money.yanit_nonrestricted_amount:.2f}")
            
            if (money.yanit_bakiye_tutar == exp_cash and 
                money.yanit_restricted_amount == exp_rest and 
                money.yanit_nonrestricted_amount == exp_nonrest):
                print("  ✅ Correct")
            else:
                print("  ❌ Incorrect")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_balance_parsing() 