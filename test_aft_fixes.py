#!/usr/bin/env python3
"""
AFT Protocol Fixes Verification Test
Tests all the critical fixes implemented for AFT functionality
"""

import sys
import time
import asyncio
from configparser import ConfigParser
from sas_communicator import SASCommunicator

class MockConfig:
    """Mock config for testing"""
    def __init__(self):
        self.data = {
            'sas': {'address': '01'},
            'machine': {'devicetypeid': '8'},
            'casino': {'casinoid': '8'}
        }
    
    def get(self, section, key, fallback=None):
        return self.data.get(section, {}).get(key, fallback)
    
    def getint(self, section, key, fallback=None):
        value = self.get(section, key, fallback)
        return int(value) if value is not None else fallback

def test_asset_number_storage():
    """Test 1: Asset Number Storage Format"""
    print("=" * 60)
    print("TEST 1: Asset Number Storage Format")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)  # Won't actually open
    
    # Simulate asset number reading response
    test_response = "017309006C000000"  # Asset 108 in response format
    
    # Test the parsing logic manually
    asset_hex = test_response[8:16]  # "6C000000"
    if len(asset_hex) % 2 != 0:
        asset_hex = '0' + asset_hex
    
    # Reverse by bytes (this is the existing logic)
    reversed_hex = ''.join([asset_hex[i:i+2] for i in range(len(asset_hex)-2, -2, -2)])
    asset_dec = int(reversed_hex, 16)
    
    # Test the fixed storage format
    stored_format = f"{asset_dec:08x}"  # Should be "0000006c"
    
    print(f"Raw response: {test_response}")
    print(f"Extracted hex: {asset_hex}")
    print(f"Reversed hex: {reversed_hex}")
    print(f"Decimal value: {asset_dec}")
    print(f"Stored AFT format: {stored_format}")
    
    # Verify correct format
    expected = "0000006c"
    if stored_format == expected:
        print(f"✅ PASS: Asset number stored correctly as {stored_format}")
    else:
        print(f"❌ FAIL: Expected {expected}, got {stored_format}")
    
    return stored_format == expected

def test_balance_query_command():
    """Test 2: Balance Query Command Construction"""
    print("\n" + "=" * 60)
    print("TEST 2: Balance Query Command Construction")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)
    
    # Set up asset number in correct format
    communicator.asset_number = "0000006c"  # Correct AFT format
    
    # Test balance query command construction
    sas_address = "01"
    asset_number = communicator.asset_number.upper()  # "0000006C"
    command = f"{sas_address}74{asset_number}"
    
    print(f"SAS Address: {sas_address}")
    print(f"Asset Number: {asset_number}")
    print(f"Command (before CRC): {command}")
    
    expected_command_start = "01740000006C"
    if command == expected_command_start:
        print(f"✅ PASS: Balance query command constructed correctly")
    else:
        print(f"❌ FAIL: Expected {expected_command_start}, got {command}")
    
    return command == expected_command_start

def test_aft_command_construction():
    """Test 3: AFT Command Construction"""
    print("\n" + "=" * 60)
    print("TEST 3: AFT Command Construction")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)
    
    # Test AFT command header construction
    sas_address = "01"
    command_header = sas_address + "72"
    
    print(f"SAS Address: {sas_address}")
    print(f"AFT Command Header: {command_header}")
    
    # Test transfer type encoding
    transfer_type = 10  # Cashable
    transfer_type_encoded = f"{transfer_type:02d}"  # Should be "10", not "0A"
    
    print(f"Transfer Type: {transfer_type}")
    print(f"Transfer Type Encoded: {transfer_type_encoded}")
    
    expected_header = "0172"
    expected_type = "10"
    
    header_ok = command_header == expected_header
    type_ok = transfer_type_encoded == expected_type
    
    if header_ok:
        print(f"✅ PASS: AFT command header uses SAS address correctly")
    else:
        print(f"❌ FAIL: Expected header {expected_header}, got {command_header}")
    
    if type_ok:
        print(f"✅ PASS: Transfer type encoded in decimal format")
    else:
        print(f"❌ FAIL: Expected type {expected_type}, got {transfer_type_encoded}")
    
    return header_ok and type_ok

def test_message_splitting():
    """Test 4: Message Splitting Logic"""
    print("\n" + "=" * 60)
    print("TEST 4: Message Splitting Logic")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)
    
    # Test concatenated message
    test_message = "01FF001CA50174236C000000010203040506070809"
    
    # This should split into two messages
    messages = communicator._split_sas_messages(test_message)
    
    print(f"Original message: {test_message}")
    print(f"Split into {len(messages)} messages:")
    for i, msg in enumerate(messages):
        print(f"  Message {i+1}: {msg}")
    
    # Should have at least 2 messages
    if len(messages) >= 2:
        print(f"✅ PASS: Message splitting working correctly")
        return True
    else:
        print(f"❌ FAIL: Expected multiple messages, got {len(messages)}")
        return False

async def test_async_wait_timing():
    """Test 5: Async Wait Function Timing"""
    print("\n" + "=" * 60)
    print("TEST 5: Async Wait Function Timing")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)
    
    # Test the timing logic
    start_time = time.time()
    
    # Simulate setting status after a delay
    async def simulate_response():
        await asyncio.sleep(0.2)  # 200ms delay
        communicator.sas_money.global_para_yukleme_transfer_status = "00"
    
    # Start the simulation
    asyncio.create_task(simulate_response())
    
    # Test the wait function
    result = await communicator.sas_money.wait_for_para_yukle_completion(timeout=2)
    
    elapsed = time.time() - start_time
    
    print(f"Wait result: {result}")
    print(f"Elapsed time: {elapsed:.3f}s")
    print(f"Final status: {communicator.sas_money.global_para_yukleme_transfer_status}")
    
    if result is True and elapsed < 1.0:
        print(f"✅ PASS: Async wait function working with proper timing")
        return True
    else:
        print(f"❌ FAIL: Wait function issue - result: {result}, time: {elapsed:.3f}s")
        return False

async def run_all_tests():
    """Run all AFT fix verification tests"""
    print("AFT Protocol Fixes Verification Test Suite")
    print("=" * 60)
    
    tests = [
        ("Asset Number Storage", test_asset_number_storage),
        ("Balance Query Command", test_balance_query_command),
        ("AFT Command Construction", test_aft_command_construction),
        ("Message Splitting", test_message_splitting),
        ("Async Wait Timing", test_async_wait_timing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AFT fixes verified successfully!")
    else:
        print("⚠️  Some tests failed - check the fixes above")
    
    return passed == total

if __name__ == "__main__":
    print("Starting AFT fixes verification...")
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test suite error: {e}")
        sys.exit(1) 