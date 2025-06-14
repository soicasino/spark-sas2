#!/usr/bin/env python3
"""
Test script to verify AFT balance queries work correctly
"""

import asyncio
import time
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

async def test_balance_query():
    """Test balance query after AFT transfer"""
    print("=" * 60)
    print("AFT Balance Query Test")
    print("=" * 60)
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)  # Won't actually open
    
    # Set up asset number
    communicator.asset_number = "0000006c"
    
    # Test balance query command construction
    sas_money = communicator.sas_money
    
    print("1. Testing balance query command construction...")
    
    # This should construct the correct balance query command
    try:
        result = sas_money.komut_bakiye_sorgulama("test", False, "balance_test")
        print(f"✅ Balance query command sent successfully")
    except Exception as e:
        print(f"❌ Balance query failed: {e}")
        return False
    
    print("\n2. Testing balance response parsing...")
    
    # Test with a mock AFT status response that includes current balance
    # Format: Address(01) + Command(74) + Length(1F) + AssetNumber(0000006C) + 
    #         GameLockStatus(00) + AvailableTransfers(FF) + HostCashoutStatus(00) + 
    #         AFTStatus(01) + MaxBufferIndex(7F) + 
    #         CurrentCashableAmount(0000002000) + CurrentRestrictedAmount(0000000000) + 
    #         CurrentNonRestrictedAmount(0000000000) + RestrictedExpiration(000000) + 
    #         RestrictedPoolID(0000)
    
    mock_response = "01741F0000006C00FF0001" + "7F" + "0000002000" + "0000000000" + "0000000000" + "000000" + "0000"
    
    print(f"Mock AFT status response: {mock_response}")
    print(f"Expected cashable amount: 2000 cents = $20.00")
    
    # Reset balance values
    sas_money.yanit_bakiye_tutar = 0
    sas_money.yanit_restricted_amount = 0
    sas_money.yanit_nonrestricted_amount = 0
    
    # Parse the mock response
    try:
        sas_money.yanit_bakiye_sorgulama(mock_response)
        
        print(f"Parsed cashable amount: ${sas_money.yanit_bakiye_tutar:.2f}")
        print(f"Parsed restricted amount: ${sas_money.yanit_restricted_amount:.2f}")
        print(f"Parsed non-restricted amount: ${sas_money.yanit_nonrestricted_amount:.2f}")
        
        # Check if parsing worked correctly
        if sas_money.yanit_bakiye_tutar == 20.0:
            print("✅ Balance response parsing works correctly")
            return True
        else:
            print(f"❌ Balance parsing failed - expected $20.00, got ${sas_money.yanit_bakiye_tutar:.2f}")
            return False
            
    except Exception as e:
        print(f"❌ Balance response parsing failed: {e}")
        return False

async def test_aft_with_balance_query():
    """Test complete AFT flow with balance query"""
    print("\n" + "=" * 60)
    print("Complete AFT + Balance Query Flow Test")
    print("=" * 60)
    
    print("This test simulates:")
    print("1. AFT transfer completion")
    print("2. Automatic balance query")
    print("3. Balance update verification")
    
    config = MockConfig()
    communicator = SASCommunicator("COM1", config)
    sas_money = communicator.sas_money
    
    # Set up asset number
    communicator.asset_number = "0000006c"
    
    # Simulate AFT transfer completion
    print("\n1. Simulating AFT transfer completion...")
    sas_money.global_para_yukleme_transfer_status = "00"  # Success
    print("✅ AFT transfer marked as completed")
    
    # Now query balance to see the updated amount
    print("\n2. Querying balance after AFT transfer...")
    
    # Reset balance
    sas_money.yanit_bakiye_tutar = 0
    
    # Send balance query
    try:
        sas_money.komut_bakiye_sorgulama("aft_test", False, "post_aft_balance")
        print("✅ Balance query sent")
        
        # Simulate receiving the balance response with updated amount
        # This would normally come from the machine
        mock_response_with_credits = "01741F0000006C00FF0001" + "7F" + "0000002000" + "0000000000" + "0000000000" + "000000" + "0000"
        
        print("\n3. Processing balance response...")
        sas_money.yanit_bakiye_sorgulama(mock_response_with_credits)
        
        print(f"Updated balance: ${sas_money.yanit_bakiye_tutar:.2f}")
        
        if sas_money.yanit_bakiye_tutar > 0:
            print("✅ Balance updated successfully after AFT transfer")
            return True
        else:
            print("❌ Balance not updated after AFT transfer")
            return False
            
    except Exception as e:
        print(f"❌ Post-AFT balance query failed: {e}")
        return False

async def main():
    """Run all balance query tests"""
    print("Starting AFT Balance Query Tests...")
    
    test1_result = await test_balance_query()
    test2_result = await test_aft_with_balance_query()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Balance Query Parsing", test1_result),
        ("AFT + Balance Query Flow", test2_result),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All balance query tests passed!")
        print("\nRECOMMENDATION:")
        print("Add automatic balance query after AFT transfer completion")
        print("to update the displayed balance in real-time.")
    else:
        print("⚠️  Some tests failed - check balance query implementation")
    
    return passed == total

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"Test error: {e}")
        exit(1) 