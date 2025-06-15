#!/usr/bin/env python3
"""
Test script to debug AFT command generation and compare with original working format.
This will help identify why coin-in meters aren't updating despite successful AFT transfers.
"""

import sys
sys.path.append('.')

from sas_communicator import SASCommunicator
from config_manager import ConfigManager
import time

def add_left_string(text, eklenecek, kacadet):
    """Original AddLeftString function"""
    while kacadet > 0:
        text = eklenecek + text
        kacadet = kacadet - 1
    return text

def add_left_bcd_original(numbers, leng):
    """Original AddLeftBCD function that was working"""
    numbers = int(numbers)
    retdata = str(numbers)
    
    if len(retdata) % 2 == 1:
        retdata = "0" + retdata
    
    count_number = len(retdata) // 2  # 1250 -> 4
    kalan = (leng - count_number)     # 5-4 = 1
    
    retdata = add_left_string(retdata, "00", int(kalan))
    
    return retdata

def create_original_aft_command(amount_cents, transaction_id, asset_number, registration_key):
    """Recreate the original working AFT command format"""
    print(f"\n🔧 Creating ORIGINAL AFT Command Format:")
    print(f"   Amount: ${amount_cents/100:.2f} ({amount_cents} cents)")
    print(f"   Transaction ID: {transaction_id}")
    print(f"   Asset Number: {asset_number}")
    
    # Original command structure
    command_header = "01"  # Address
    command_header += "72"  # Command
    # Length will be added later
    
    command = ""
    command += "00"  # Transfer Code
    command += "00"  # Transfer Index
    command += "00"  # Transfer Type (cashable)
    
    # BCD amounts (original format)
    command += add_left_bcd_original(amount_cents, 5)  # Cashable amount
    command += add_left_bcd_original(0, 5)             # Restricted amount
    command += "0000000000"                            # Non-restricted amount
    
    command += "07"  # Transfer flag (hard cashout)
    command += asset_number  # Asset number
    command += registration_key  # Registration key
    
    # Transaction ID (original format)
    transaction_id_hex = "".join("{:02x}".format(ord(c)) for c in str(transaction_id))
    command += add_left_bcd_original(len(transaction_id_hex) // 2, 1)  # Length
    command += transaction_id_hex  # Transaction ID
    
    command += "00000000"  # Expiration Date
    command += "0000"      # Pool ID
    command += "00"        # Receipt data length
    
    # Calculate length (original method)
    command_length = hex(len(command) // 2).replace("0x", "")
    command_header += command_length
    
    full_command = command_header + command
    print(f"   Command (no CRC): {full_command}")
    print(f"   Command Length: {len(command) // 2} bytes")
    
    return full_command

def test_aft_command_generation():
    """Test AFT command generation and show exact hex commands"""
    print("=" * 60)
    print("AFT Command Generation Debug Test")
    print("=" * 60)
    
    # Create test instance with proper config
    config = ConfigManager()
    config.set('sas', 'address', '01')
    config.set('sas', 'assetnumber', '0000006c')
    config.set('sas', 'registrationkey', '0000000000000000000000000000000000000000')
    
    comm = SASCommunicator('COM1', config)
    comm.asset_number = '0000006c'
    
    print(f"Asset Number: {comm.asset_number}")
    print(f"Registration Key: {config.get('sas', 'registrationkey')}")
    
    # Test case: $5.00 transfer
    amount = 5.00
    amount_cents = int(amount * 100)
    transaction_id = 500
    
    print(f"\n--- Testing ${amount:.2f} AFT Transfer ---")
    
    # Create original format command
    original_command = create_original_aft_command(
        amount_cents, 
        transaction_id,
        '0000006c',
        '0000000000000000000000000000000000000000'
    )
    
    # Generate current format command
    print(f"\n🔧 Creating CURRENT AFT Command Format:")
    try:
        result = comm.sas_money.komut_para_yukle(
            doincreasetransactionid=0,  # Don't auto-increment
            transfertype=10,
            customerbalance=amount,
            customerpromo=0.00,
            transactionid=transaction_id,
            assetnumber='0000006c',
            registrationkey='0000000000000000000000000000000000000000'
        )
        print(f"✅ Current command generated successfully")
        print(f"Transaction ID returned: {result}")
        
    except Exception as e:
        print(f"❌ Error generating current command: {e}")
    
    return True

def analyze_differences():
    """Analyze the key differences between original and current formats"""
    print("\n" + "=" * 60)
    print("🔍 CRITICAL DIFFERENCES ANALYSIS")
    print("=" * 60)
    
    print("1. COMMAND LENGTH CALCULATION:")
    print("   Original: hex(int(len(Command)/2)).replace('0x','')")
    print("   Current:  f'{command_length:02X}'")
    print("   ⚠️  Potential issue: Case sensitivity, padding")
    
    print("\n2. BCD AMOUNT FORMATTING:")
    print("   Original: AddLeftBCD(amount_cents, 5)")
    print("   Current:  _add_left_bcd(str(amount_cents), 5)")
    print("   ⚠️  Potential issue: Different padding logic")
    
    print("\n3. TRANSACTION ID ENCODING:")
    print("   Original: ''.join('{:02x}'.format(ord(c)) for c in str(id))")
    print("   Current:  ''.join('{:02x}'.format(ord(c)) for c in str(id))")
    print("   ✅ Should be the same")
    
    print("\n4. TRANSFER TYPE:")
    print("   Original: '00' for cashable")
    print("   Current:  '10' for cashable")
    print("   🚨 MAJOR DIFFERENCE! This could be the issue!")
    
    print("\n5. ASSET NUMBER FORMAT:")
    print("   Original: Direct from config")
    print("   Current:  May have formatting differences")

def main():
    print("🔍 AFT Command Debug Analysis")
    print("This script will help identify why coin-in meters aren't updating")
    print("despite successful AFT transfer acknowledgments.\n")
    
    try:
        # Test command generation
        test_aft_command_generation()
        
        # Analyze differences
        analyze_differences()
        
        print("\n" + "=" * 60)
        print("🎯 KEY FINDINGS:")
        print("=" * 60)
        print("1. Transfer Type codes may be different!")
        print("   - Original uses '00' for cashable")
        print("   - Current uses '10' for cashable")
        print("2. BCD formatting might have subtle differences")
        print("3. Command length calculation method differs")
        
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. ✅ Check transfer type codes in current implementation")
        print("2. ✅ Verify BCD formatting matches original exactly")
        print("3. ✅ Test with original command format")
        print("4. ✅ Monitor actual hex commands being sent")
        
        print("\n🚨 HYPOTHESIS:")
        print("The machine accepts the AFT commands (returns success)")
        print("but doesn't apply them to coin-in meters because:")
        print("- Transfer type code mismatch")
        print("- BCD formatting issues")
        print("- Command structure differences")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 