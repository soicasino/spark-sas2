#!/usr/bin/env python3
"""
AFT Balance API Test

This script tests AFT balance through the existing FastAPI endpoints
without opening a new SAS port connection.
"""

import requests
import json
import time

class AFTBalanceAPITester:
    """Test AFT balance using existing API endpoints"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def test_current_balance(self):
        """Test current AFT balance"""
        print("📊 Testing current AFT balance...")
        
        try:
            response = requests.get(f"{self.base_url}/api/money/balance")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Balance query successful!")
                print(f"   Cashable: ${data['data']['cashable_balance']:.2f}")
                print(f"   Restricted: ${data['data']['restricted_balance']:.2f}")
                print(f"   Non-restricted: ${data['data']['nonrestricted_balance']:.2f}")
                print(f"   Total: ${data['data']['total_balance']:.2f}")
                return data['data']
            else:
                print(f"❌ Balance query failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error querying balance: {e}")
            return None

    def test_small_transfer(self):
        """Test a small AFT transfer"""
        print("💰 Testing small AFT transfer ($1.00)...")
        
        try:
            transfer_data = {
                "amount": 1.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/money/add-credits",
                json=transfer_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Transfer successful!")
                print(f"   Amount: ${data['data']['amount']:.2f}")
                print(f"   Transaction ID: {data['data']['transaction_id']}")
                print(f"   Status: {data['data']['status']}")
                print(f"   Execution time: {data['execution_time_ms']:.1f}ms")
                return data['data']
            else:
                print(f"❌ Transfer failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error during transfer: {e}")
            return None

    def run_balance_investigation(self):
        """Run complete balance investigation"""
        
        print("🚀 Starting AFT Balance Investigation...")
        print("=" * 60)
        
        # Step 1: Check initial balance
        print("\n📊 STEP 1: Check initial balance")
        initial_balance = self.test_current_balance()
        
        # Step 2: Perform a small transfer
        print("\n💰 STEP 2: Perform small transfer")
        transfer_result = self.test_small_transfer()
        
        if not transfer_result:
            print("❌ Transfer failed, cannot continue investigation")
            return
        
        # Step 3: Wait a moment for processing
        print("\n⏳ STEP 3: Waiting for processing...")
        time.sleep(2)
        
        # Step 4: Check balance after transfer
        print("\n📊 STEP 4: Check balance after transfer")
        final_balance = self.test_current_balance()
        
        # Step 5: Analysis
        print("\n🔍 STEP 5: Analysis")
        print("=" * 60)
        
        if initial_balance and final_balance:
            initial_total = initial_balance['total_balance']
            final_total = final_balance['total_balance']
            expected_total = initial_total + 1.0
            
            print(f"Initial balance: ${initial_total:.2f}")
            print(f"Transfer amount: $1.00")
            print(f"Expected balance: ${expected_total:.2f}")
            print(f"Actual balance: ${final_total:.2f}")
            
            if final_total > initial_total:
                difference = final_total - initial_total
                print(f"✅ SUCCESS: Balance increased by ${difference:.2f}")
            elif final_total == initial_total:
                print("🤔 ISSUE: Balance unchanged after successful transfer")
                print("\nPossible explanations:")
                print("1. AFT credits are in separate pool from balance query")
                print("2. Machine design keeps AFT and coin-in pools separate")
                print("3. Balance query (74h) doesn't include AFT credit pool")
                print("4. AFT credits available for play but not in 'balance'")
            else:
                print("❓ UNEXPECTED: Balance decreased")
        
        # Step 6: Additional investigation
        print("\n🔬 STEP 6: Additional investigation")
        
        # Try multiple balance queries to see if there's a delay
        print("Trying multiple balance queries...")
        for i in range(3):
            print(f"  Query {i+1}:")
            balance = self.test_current_balance()
            if balance:
                print(f"    Total: ${balance['total_balance']:.2f}")
            time.sleep(1)
        
        print("\n✅ AFT Balance Investigation Complete!")

def main():
    """Main test function"""
    tester = AFTBalanceAPITester()
    tester.run_balance_investigation()

if __name__ == "__main__":
    main() 