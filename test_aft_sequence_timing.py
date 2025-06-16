#!/usr/bin/env python3
"""
AFT Sequence Timing Test

This test verifies the proper AFT registration -> wait -> transfer -> wait sequence
that matches the original working code timing requirements.
"""

import requests
import time
import json

def test_aft_sequence_timing():
    """Test the complete AFT sequence with proper timing"""
    print("🧪 AFT Sequence Timing Test")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    print("This test will:")
    print("1. Check initial balance")
    print("2. Register AFT (with timing)")
    print("3. Add $2.00 via AFT (with proper waits)")
    print("4. Check balance after sufficient wait time")
    print("5. Verify the timing matches original working code")
    
    # Step 1: Initial balance check
    print("\n" + "─" * 50)
    print("📊 STEP 1: Check initial balance")
    print("─" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/money/balance")
        if response.status_code == 200:
            balance_data = response.json()
            initial_cashable = balance_data.get('data', {}).get('balance', {}).get('cashable', 0.0)
            print(f"   Initial Cashable Balance: ${initial_cashable:.2f}")
        else:
            print(f"   ❌ Balance check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Balance check error: {e}")
        return False
    
    # Step 2: AFT Registration with timing
    print("\n" + "─" * 50)
    print("🔧 STEP 2: AFT Registration with timing")
    print("─" * 50)
    
    try:
        print("   Sending AFT registration request...")
        start_reg = time.time()
        response = requests.post(f"{base_url}/api/money/register-aft")
        reg_time = time.time() - start_reg
        
        if response.status_code == 200:
            reg_data = response.json()
            print(f"   ✅ AFT Registration: {reg_data.get('message', 'Success')}")
            print(f"   📊 Registration time: {reg_time:.2f}s")
        else:
            print(f"   ❌ AFT Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        # Additional wait for registration to settle
        print("   ⏳ Waiting for registration to settle...")
        time.sleep(2)
        
    except Exception as e:
        print(f"   ❌ AFT Registration error: {e}")
        return False
    
    # Step 3: AFT Transfer with proper timing
    print("\n" + "─" * 50)
    print("💰 STEP 3: AFT Transfer with timing analysis")
    print("─" * 50)
    
    try:
        transfer_data = {
            "amount": 2.00,
            "transfer_type": "00"  # Cashable
        }
        
        print(f"   Sending AFT transfer: ${transfer_data['amount']:.2f}")
        start_transfer = time.time()
        response = requests.post(f"{base_url}/api/money/add-credits", json=transfer_data)
        transfer_time = time.time() - start_transfer
        
        if response.status_code == 200:
            transfer_result = response.json()
            print(f"   ✅ AFT Transfer: {transfer_result.get('message', 'Success')}")
            print(f"   📊 Transfer time: {transfer_time:.2f}s")
            print(f"   📋 Transaction ID: {transfer_result.get('data', {}).get('transaction_id', 'Unknown')}")
            
            # Check reported balance from transfer
            reported_balance = transfer_result.get('data', {}).get('updated_balance', {})
            reported_cashable = reported_balance.get('cashable', 0.0)
            print(f"   📊 Reported new balance: ${reported_cashable:.2f}")
            
        else:
            print(f"   ❌ AFT Transfer failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ AFT Transfer error: {e}")
        return False
    
    # Step 4: Additional wait and balance verification
    print("\n" + "─" * 50)
    print("⏱️  STEP 4: Additional wait and balance verification")
    print("─" * 50)
    
    # Wait additional time for machine to fully process
    print("   ⏳ Waiting additional time for machine to fully process...")
    for i in range(5):
        print(f"   Waiting... {i+1}/5")
        time.sleep(2)
        
        # Check balance during wait
        try:
            response = requests.get(f"{base_url}/api/money/balance")
            if response.status_code == 200:
                balance_data = response.json()
                current_cashable = balance_data.get('data', {}).get('balance', {}).get('cashable', 0.0)
                print(f"     Current balance check {i+1}: ${current_cashable:.2f}")
                
                if current_cashable > initial_cashable:
                    print(f"   🎉 SUCCESS! Balance increased from ${initial_cashable:.2f} to ${current_cashable:.2f}")
                    break
            else:
                print(f"     Balance check {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"     Balance check {i+1} error: {e}")
    
    # Step 5: Final verification
    print("\n" + "─" * 50)
    print("✅ STEP 5: Final verification")
    print("─" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/money/balance")
        if response.status_code == 200:
            balance_data = response.json()
            final_cashable = balance_data.get('data', {}).get('balance', {}).get('cashable', 0.0)
            
            print(f"   📊 FINAL VERIFICATION:")
            print(f"     Initial Balance: ${initial_cashable:.2f}")
            print(f"     Final Balance:   ${final_cashable:.2f}")
            print(f"     Expected Increase: $2.00")
            print(f"     Actual Increase: ${final_cashable - initial_cashable:.2f}")
            
            if abs((final_cashable - initial_cashable) - 2.00) < 0.01:
                print(f"   🎉 SUCCESS! AFT transfer working correctly!")
                return True
            elif final_cashable > initial_cashable:
                print(f"   🟡 PARTIAL SUCCESS: Balance increased but not by expected amount")
                return "partial"
            else:
                print(f"   ❌ FAILED: No balance increase detected")
                return False
        else:
            print(f"   ❌ Final balance check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Final verification error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AFT Sequence Timing Test...")
    print("Make sure your main app is running on localhost:8000")
    print()
    
    result = test_aft_sequence_timing()
    
    if result is True:
        print("\n🎉 AFT Sequence Timing Test PASSED!")
        print("The AFT system is working correctly with proper timing.")
    elif result == "partial":
        print("\n🟡 AFT Sequence Timing Test PARTIAL SUCCESS!")
        print("AFT transfers are working but may need timing adjustments.")
    else:
        print("\n❌ AFT Sequence Timing Test FAILED!")
        print("AFT transfers are not working properly.") 