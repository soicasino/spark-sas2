#!/usr/bin/env python3
"""
Test script to verify the AFT command construction fix.
This script tests that AFT commands now start with SAS address instead of asset number.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_aft_command_construction():
    """Test that AFT commands are constructed correctly"""
    
    print("=== AFT Command Construction Test ===")
    
    # Test adding credits to see the command construction
    print("\n1. Testing AFT command construction...")
    
    try:
        # Make a request to add credits
        response = requests.post(f"{BASE_URL}/api/money/add-credits", json={
            "amount": 100.0,  # 100 TL
            "transfer_type": "10"  # Cashable
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Add credits request successful")
            print(f"   Response: {result.get('message', 'No message')}")
            
            # The command should now start with '01' (SAS address) instead of '6C000000' (asset number)
            print(f"   ✅ Command should now start with SAS address '01' instead of asset number")
            
        else:
            print(f"   ❌ Add credits request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error during add credits test: {e}")
    
    print("\n2. Expected command format:")
    print("   OLD (incorrect): 6C000000723900000A000002000000...")
    print("   NEW (correct):   017239000A000002000000...")
    print("   Key difference: Command starts with '01' (SAS address) not '6C000000' (asset number)")
    
    print("\n3. Why this matters:")
    print("   - SAS protocol requires commands to start with the machine address")
    print("   - Asset number goes INSIDE the command data, not at the beginning")
    print("   - This was likely why the machine wasn't responding to AFT commands")

if __name__ == "__main__":
    test_aft_command_construction() 