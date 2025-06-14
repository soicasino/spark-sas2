#!/usr/bin/env python3
"""
Test script for BCD encoding verification.
This script tests the new BCD encoding implementation against known values.
"""

from utils import add_left_bcd, to_bcd

def test_bcd_encoding():
    """Test BCD encoding with various values"""
    
    print("=== BCD Encoding Test ===")
    
    # Test cases: (input_value, expected_length_bytes, expected_result)
    test_cases = [
        # Basic cases
        (1234, 5, "0000001234"),      # 1234 cents = $12.34
        (20000, 5, "0000020000"),     # 20000 cents = $200.00
        (123456, 5, "0000123456"),    # 123456 cents = $1234.56
        (5, 5, "0000000005"),         # 5 cents = $0.05
        (0, 5, "0000000000"),         # 0 cents = $0.00
        
        # Edge cases
        (9999999999, 5, "9999999999"), # Max 5-byte value
        (1, 2, "0001"),               # Small value, small length
        (12, 3, "000012"),            # Even digits
        (123, 3, "000123"),           # Odd digits
    ]
    
    print("\n1. Testing add_left_bcd function:")
    for i, (input_val, length_bytes, expected) in enumerate(test_cases):
        try:
            result = add_left_bcd(str(input_val), length_bytes)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"   Test {i+1}: {input_val} -> {result} (expected: {expected}) {status}")
            
            if result != expected:
                print(f"      ERROR: Expected {expected}, got {result}")
                
        except Exception as e:
            print(f"   Test {i+1}: {input_val} -> ERROR: {e}")
    
    print("\n2. Testing to_bcd function:")
    for i, (input_val, length_bytes, expected) in enumerate(test_cases):
        try:
            result = to_bcd(input_val, length_bytes)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"   Test {i+1}: {input_val} -> {result} (expected: {expected}) {status}")
            
            if result != expected:
                print(f"      ERROR: Expected {expected}, got {result}")
                
        except Exception as e:
            print(f"   Test {i+1}: {input_val} -> ERROR: {e}")
    
    print("\n3. Testing real-world AFT amounts:")
    real_world_cases = [
        (20000, "200.00 TL"),  # 200 TL = 20000 cents
        (50000, "500.00 TL"),  # 500 TL = 50000 cents
        (10050, "100.50 TL"),  # 100.50 TL = 10050 cents
        (1, "0.01 TL"),        # 1 cent
        (99999, "999.99 TL"),  # 999.99 TL
    ]
    
    for amount_cents, description in real_world_cases:
        bcd_result = add_left_bcd(str(amount_cents), 5)
        print(f"   {description} ({amount_cents} cents) -> BCD: {bcd_result}")
    
    print("\n4. Verifying BCD format correctness:")
    # Test that each nibble is a valid decimal digit (0-9)
    test_value = 123456
    bcd_result = add_left_bcd(str(test_value), 5)
    print(f"   Testing value: {test_value}")
    print(f"   BCD result: {bcd_result}")
    print(f"   Length: {len(bcd_result)} characters ({len(bcd_result)//2} bytes)")
    
    # Check each nibble
    valid_bcd = True
    for i, char in enumerate(bcd_result):
        nibble_value = int(char, 16)
        if nibble_value > 9:
            print(f"   ❌ Invalid BCD nibble at position {i}: {char} (value: {nibble_value})")
            valid_bcd = False
    
    if valid_bcd:
        print(f"   ✅ All nibbles are valid BCD (0-9)")
    
    print("\n5. Comparing with old implementation:")
    # Simulate old implementation (just hex conversion)
    def old_add_left_bcd(number_str, length_bytes):
        number_str = str(int(number_str))
        if len(number_str) % 2 != 0:
            number_str = "0" + number_str
        current_len_bytes = len(number_str) // 2
        padding_needed_bytes = length_bytes - current_len_bytes
        return "00" * int(padding_needed_bytes) + number_str
    
    test_amount = 20000  # 200.00 TL
    old_result = old_add_left_bcd(str(test_amount), 5)
    new_result = add_left_bcd(str(test_amount), 5)
    
    print(f"   Amount: {test_amount} cents (200.00 TL)")
    print(f"   Old implementation: {old_result}")
    print(f"   New implementation: {new_result}")
    print(f"   Same result: {'✅ YES' if old_result == new_result else '❌ NO'}")
    
    if old_result != new_result:
        print(f"   ⚠️  BCD encoding has been fixed! The old implementation was incorrect.")
        print(f"   ⚠️  This might explain why AFT commands weren't being processed.")

if __name__ == "__main__":
    test_bcd_encoding() 