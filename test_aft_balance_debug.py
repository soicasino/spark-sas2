#!/usr/bin/env python3
"""
AFT Balance Debug Test

This script investigates why AFT balance shows $0.00 after successful transfers.
We'll examine the actual SAS responses and balance parsing logic.
"""

import sys
import os
import time
import asyncio
from config_manager import ConfigManager
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

class AFTBalanceDebugger:
    """Debug AFT balance parsing issues"""

    def __init__(self):
        self.config = ConfigManager()
        self.communicator = None
        self.money = None

    def setup_sas_communication(self):
        """Initialize SAS communication"""
        try:
            print("🔧 Setting up SAS communication...")
            
            # Initialize SAS communicator
            self.communicator = SASCommunicator(self.config)
            
            # Initialize money functions
            self.money = SasMoney(self.config, self.communicator)
            self.communicator.sas_money = self.money
            
            print("✅ SAS communication setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up SAS communication: {e}")
            return False

    async def debug_balance_query(self):
        """Debug the balance query process step by step"""
        
        print("\\n" + "="*60)
        print("AFT BALANCE DEBUG - STEP BY STEP ANALYSIS")
        print("="*60)
        
        # Step 1: Send balance query and capture raw response
        print("\\n📊 STEP 1: Sending balance query...")
        
        # Reset balance values to see if they change
        original_cashable = self.money.yanit_bakiye_tutar
        original_restricted = self.money.yanit_restricted_amount
        original_nonrestricted = self.money.yanit_nonrestricted_amount
        
        print(f"[DEBUG] Before query - Cashable: ${original_cashable}, Restricted: ${original_restricted}, Non-restricted: ${original_nonrestricted}")
        
        # Send balance query
        self.money.komut_bakiye_sorgulama("debug_test", False, "balance_debug")
        
        # Wait for response
        print("[DEBUG] Waiting for balance response...")
        balance_result = await self.money.wait_for_bakiye_sorgulama_completion(timeout=8)
        
        # Check results
        new_cashable = self.money.yanit_bakiye_tutar
        new_restricted = self.money.yanit_restricted_amount
        new_nonrestricted = self.money.yanit_nonrestricted_amount
        
        print(f"[DEBUG] After query - Cashable: ${new_cashable}, Restricted: ${new_restricted}, Non-restricted: ${new_nonrestricted}")
        print(f"[DEBUG] Balance query result: {balance_result}")
        
        # Step 2: Check if there are any AFT-specific balance fields we're missing
        print("\\n🔍 STEP 2: Checking for additional AFT balance fields...")
        
        # Check communicator for any stored balance information
        if hasattr(self.communicator, 'last_game_lock_status'):
            print(f"[DEBUG] Game Lock Status: {self.communicator.last_game_lock_status}")
            print(f"[DEBUG] AFT Status: {getattr(self.communicator, 'last_aft_status', 'Not available')}")
            print(f"[DEBUG] Available Transfers: {getattr(self.communicator, 'last_available_transfers', 'Not available')}")
        
        # Step 3: Try alternative balance query methods
        print("\\n🔄 STEP 3: Trying alternative balance queries...")
        
        # Try querying with different parameters
        print("[DEBUG] Trying balance query with different asset number...")
        
        # Store original asset number
        original_asset = getattr(self.communicator, 'asset_number', None)
        
        # Try with known working asset number
        self.communicator.asset_number = "0000006C"
        
        self.money.komut_bakiye_sorgulama("debug_alt", False, "alternative_balance")
        alt_result = await self.money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        alt_cashable = self.money.yanit_bakiye_tutar
        alt_restricted = self.money.yanit_restricted_amount
        alt_nonrestricted = self.money.yanit_nonrestricted_amount
        
        print(f"[DEBUG] Alternative query - Cashable: ${alt_cashable}, Restricted: ${alt_restricted}, Non-restricted: ${alt_nonrestricted}")
        print(f"[DEBUG] Alternative query result: {alt_result}")
        
        # Restore original asset number
        if original_asset:
            self.communicator.asset_number = original_asset
        
        # Step 4: Check if the issue is with BCD parsing
        print("\\n🧮 STEP 4: Testing BCD parsing...")
        
        # Test BCD conversion with known values
        test_values = [
            ("0000000500", "Should be $5.00"),
            ("0000001000", "Should be $10.00"),
            ("0000002000", "Should be $20.00"),
            ("0000000000", "Should be $0.00"),
        ]
        
        for bcd_value, description in test_values:
            try:
                parsed_value = self.money.bcd_to_int(bcd_value) / 100
                print(f"[DEBUG] BCD '{bcd_value}' -> ${parsed_value:.2f} ({description})")
            except Exception as e:
                print(f"[DEBUG] BCD parsing error for '{bcd_value}': {e}")
        
        return {
            "original_balance": {
                "cashable": original_cashable,
                "restricted": original_restricted,
                "nonrestricted": original_nonrestricted
            },
            "final_balance": {
                "cashable": new_cashable,
                "restricted": new_restricted,
                "nonrestricted": new_nonrestricted
            },
            "balance_query_success": balance_result,
            "alternative_query_success": alt_result
        }

    async def run_debug_test(self):
        """Run the complete AFT balance debug test"""
        
        print("🚀 Starting AFT Balance Debug Test...")
        
        # Setup
        if not self.setup_sas_communication():
            print("❌ Failed to setup SAS communication")
            return False
        
        try:
            # Run debug analysis
            results = await self.debug_balance_query()
            
            print("\\n" + "="*60)
            print("DEBUG TEST RESULTS")
            print("="*60)
            
            print(f"✅ Original Balance: ${results['original_balance']['cashable']:.2f}")
            print(f"✅ Final Balance: ${results['final_balance']['cashable']:.2f}")
            print(f"✅ Balance Query Success: {results['balance_query_success']}")
            print(f"✅ Alternative Query Success: {results['alternative_query_success']}")
            
            # Analysis
            if results['final_balance']['cashable'] > 0:
                print("\\n🎉 SUCCESS: AFT balance is being read correctly!")
            else:
                print("\\n🤔 ISSUE: AFT balance is still $0.00")
                print("\\nPossible causes:")
                print("1. AFT transfers are in a separate pool not queried by 74h command")
                print("2. Machine requires different command to query AFT credit balance")
                print("3. AFT credits are available for play but not reflected in balance query")
                print("4. Machine design separates AFT pool from coin-in/balance pools")
            
            return True
            
        except Exception as e:
            print(f"❌ Debug test error: {e}")
            return False
        
        finally:
            # Cleanup
            if self.communicator and hasattr(self.communicator, 'close'):
                self.communicator.close()

async def main():
    """Main test function"""
    debugger = AFTBalanceDebugger()
    success = await debugger.run_debug_test()
    
    if success:
        print("\\n✅ AFT Balance Debug Test completed successfully")
    else:
        print("\\n❌ AFT Balance Debug Test failed")

if __name__ == "__main__":
    asyncio.run(main()) 