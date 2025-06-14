#!/usr/bin/env python3
"""
Test script for AFT registration process.
This script tests the new AFT registration implementation.
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8000"

async def test_aft_registration():
    """Test the AFT registration process"""
    
    print("=== AFT Registration Test ===")
    
    # Step 1: Check current AFT debug status
    print("\n1. Checking current AFT debug status...")
    try:
        response = requests.get(f"{BASE_URL}/api/money/aft-debug")
        if response.status_code == 200:
            debug_data = response.json()
            print(f"   Current AFT status: {debug_data.get('data', {}).get('aft_protocol_status', {}).get('current_status', 'unknown')}")
            print(f"   Asset number: {debug_data.get('data', {}).get('asset_number', {})}")
        else:
            print(f"   Error getting debug status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 2: Perform AFT registration
    print("\n2. Performing AFT registration...")
    try:
        response = requests.post(f"{BASE_URL}/api/money/register-aft")
        if response.status_code == 200:
            reg_data = response.json()
            print(f"   Registration successful: {reg_data.get('message')}")
            print(f"   Asset number used: {reg_data.get('data', {}).get('asset_number')}")
        else:
            print(f"   Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 3: Wait and check status again
    print("\n3. Waiting 2 seconds and checking status again...")
    await asyncio.sleep(2)
    
    try:
        response = requests.get(f"{BASE_URL}/api/money/aft-debug")
        if response.status_code == 200:
            debug_data = response.json()
            new_status = debug_data.get('data', {}).get('aft_protocol_status', {}).get('current_status', 'unknown')
            print(f"   New AFT status: {new_status}")
            
            # Check if registration was successful
            if new_status == "01":
                print("   ✅ AFT registration successful!")
            elif new_status == "00":
                print("   ⏳ AFT registration ready (may need completion)")
            elif new_status == "80":
                print("   ❌ AFT not registered")
            else:
                print(f"   ❓ Unknown status: {new_status}")
                
            # Show recommendations
            recommendations = debug_data.get('data', {}).get('recommendations', [])
            if recommendations:
                print("   Recommendations:")
                for rec in recommendations:
                    print(f"     - {rec}")
        else:
            print(f"   Error getting debug status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Test a small credit transfer
    print("\n4. Testing small credit transfer (10 TL)...")
    try:
        transfer_data = {
            "amount": 10.0,
            "transfer_type": "10"  # Cashable
        }
        response = requests.post(f"{BASE_URL}/api/money/add-credits", json=transfer_data)
        if response.status_code == 200:
            transfer_result = response.json()
            print(f"   Transfer initiated: {transfer_result.get('message')}")
            print(f"   Transfer status: {transfer_result.get('data', {}).get('transfer_status')}")
        else:
            print(f"   Transfer failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_aft_registration()) 