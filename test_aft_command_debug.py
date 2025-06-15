#!/usr/bin/env python3
"""
Test script to debug AFT command generation and compare with original working format.
This will help identify why coin-in meters aren't updating despite successful AFT transfers.
"""

import sys
sys.path.append('.')

from sas_communicator import SASCommunicator
from config import Config
import time

def test_aft_command_generation():
    """Test AFT command generation and show exact hex commands"""
    print("=" * 60)
    print("AFT Command Generation Debug Test")
    print("=" * 60)
    
    # Create test instance
    config = Config()
    comm = SASCommunicator('COM1', config)
    comm.asset_number = '0000006c'
    
    print(f"Asset Number: {comm.asset_number}")
    print(f"Registration Key: {config.get('sas', 'registrationkey')}")
    
    # Test different transfer amounts and types
    test_cases = [
        {"amount": 1.00, "type": 10, "desc": "$1.00 Cashable"},
        {"amount": 5.00, "type": 10, "desc": "$5.00 Cashable"},
        {"amount": 10.00, "type": 11, "desc": "$10.00 Restricted"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['desc']} ---")
        
        # Generate AFT command
        try:
            result = comm.sas_money.komut_para_yukle(
                doincreasetransactionid=1,
                transfertype=test_case['type'],
                customerbalance=test_case['amount'],
                customerpromo=0.00,
                transactionid=0,
                assetnumber='0000006c',
                registrationkey='0000000000000000000000000000000000000000'
            )
            print(f"✅ Command generated successfully")
            print(f"Transaction ID: {result}")
            
        except Exception as e:
            print(f"❌ Error generating command: {e}")
    
    # Show current transaction ID state
    print(f"\nCurrent Transaction ID: {comm.sas_money.current_transaction_id}")
    
    return True

def compare_with_original_format():
    """Compare our command format with the original working format"""
    print("\n" + "=" * 60)
    print("Original vs Current Command Format Comparison")
    print("=" * 60)
    
    print("ORIGINAL WORKING FORMAT (from raspberryPython_orj.py):")
    print("- Command length: hex(int(len(Command)/2))")
    print("- BCD formatting: AddLeftBCD() function")
    print("- Transaction ID: hex conversion with proper padding")
    print("- CRC: GetCRC() with byte reversal")
    print("- Structure: Header + Length + Command + CRC")
    
    print("\nCURRENT FORMAT ISSUES TO CHECK:")
    print("1. Command length calculation")
    print("2. BCD amount formatting")
    print("3. Transaction ID hex conversion")
    print("4. Asset number format")
    print("5. CRC calculation method")
    
    # Show what we expect vs what we're sending
    print("\nEXPECTED COMMAND STRUCTURE:")
    print("01 72 [LEN] [TRANSFER_TYPE] [CASHABLE_BCD] [RESTRICTED_BCD] [NON_RESTRICTED_BCD]")
    print("[TRANSFER_FLAGS] [ASSET_NUMBER] [REG_KEY] [TRANSACTION_ID_LEN] [TRANSACTION_ID]")
    print("[EXPIRATION] [POOL_ID] [RECEIPT_LEN] [CRC]")

if __name__ == "__main__":
    print("🔍 AFT Command Debug Analysis")
    print("This script will help identify why coin-in meters aren't updating")
    print("despite successful AFT transfer acknowledgments.\n")
    
    try:
        # Test command generation
        test_aft_command_generation()
        
        # Compare formats
        compare_with_original_format()
        
        print("\n" + "=" * 60)
        print("🎯 KEY INVESTIGATION POINTS:")
        print("=" * 60)
        print("1. Are AFT commands properly formatted?")
        print("2. Is the machine actually applying the transfers?")
        print("3. Are we missing a required AFT setup step?")
        print("4. Does the machine need additional confirmation?")
        print("5. Is there a difference between 'acknowledged' and 'applied'?")
        
        print("\n💡 NEXT STEPS:")
        print("- Check actual hex commands in logs")
        print("- Compare with original working commands")
        print("- Verify machine AFT configuration")
        print("- Test with different transfer types")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 