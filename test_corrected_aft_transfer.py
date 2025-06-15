#!/usr/bin/env python3
"""
Corrected AFT Transfer Test

This script tests the CORRECTED AFT transfer function that now matches
the exact format and logic from the original working raspberryPython_orj.py code.

Key corrections made:
1. Proper command length calculation
2. Exact BCD formatting from original
3. Correct transaction ID hex conversion
4. Proper CRC calculation with byte reversal
5. Exact command structure matching original
"""

import sys
import os
import time
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney

def get_machine_status_via_api():
    """Get current machine status via API"""
    try:
        response = requests.get("http://localhost:8000/api/machine/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {})
        else:
            print(f"API Status Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def print_machine_status(status_data, title="Machine Status"):
    """Print machine status with corrected SAS protocol understanding"""
    if not status_data:
        print(f"❌ No {title.lower()} data available")
        return
    
    lock_status = status_data.get('lock_status', 'Unknown')
    aft_status = status_data.get('aft_status', 'Unknown')
    is_locked = status_data.get('is_locked', 'Unknown')
    
    print(f"\n📊 {title.upper()}:")
    print(f"   Lock Status: {lock_status}")
    print(f"   AFT Status:  {aft_status}")
    print(f"   Is Locked:   {is_locked}")
    
    # Corrected interpretation: FF = NOT LOCKED, 00 = LOCKED
    if lock_status == "FF":
        print(f"   ✅ Machine is AVAILABLE (FF = not locked)")
    elif lock_status == "00":
        print(f"   🔒 Machine is LOCKED (00 = locked)")
    else:
        print(f"   ⚠️  Machine status: {lock_status}")
    
    if aft_status == "B0":
        print(f"   🎯 AFT is ENABLED but restricted (normal operation)")
    elif aft_status == "01":
        print(f"   ✅ AFT is FULLY ENABLED")
    elif aft_status == "00":
        print(f"   ❌ AFT is DISABLED")
    else:
        print(f"   ❓ AFT status: {aft_status}")

def test_corrected_aft_transfer():
    """Test the corrected AFT transfer function"""
    print("=" * 80)
    print("🔧 CORRECTED AFT TRANSFER TEST")
    print("=" * 80)
    print("Testing AFT transfer with CORRECTED command format")
    print("Based on exact logic from original working code")
    print()
    
    try:
        print("🔧 Initializing SAS communication...")
        sas_comm = SASCommunicator()
        
        if not sas_comm.is_port_open:
            print("❌ Failed to open SAS communication port")
            return False
        
        print("✅ SAS communication initialized")
        sas_money = SasMoney(sas_comm)
        print("✅ SAS money functions initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize SAS communication: {e}")
        return False
    
    try:
        # Step 1: Check initial status
        print("\n" + "─" * 60)
        print("📊 STEP 1: Check initial machine status")
        print("─" * 60)
        
        initial_status = get_machine_status_via_api()
        print_machine_status(initial_status, "Initial Status")
        
        # Step 2: AFT Registration (required)
        print("\n" + "─" * 60)
        print("🔧 STEP 2: AFT Registration")
        print("─" * 60)
        
        asset_number = "0000006C"  # Known asset number (108 decimal)
        registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex
        pos_id = "POS1"
        
        print(f"Registering AFT with asset number: {asset_number}")
        try:
            reg_result = sas_money.komut_aft_registration(asset_number, registration_key, pos_id)
            print(f"AFT Registration result: {reg_result}")
            time.sleep(2)
        except Exception as e:
            print(f"AFT Registration failed: {e}")
            print("Continuing with transfer test anyway...")
        
        # Step 3: Test Corrected AFT Transfer
        print("\n" + "─" * 60)
        print("💰 STEP 3: Corrected AFT Transfer Test")
        print("─" * 60)
        print("Using CORRECTED AFT transfer function with exact original format")
        
        # Reset transfer status
        sas_money.global_para_yukleme_transfer_status = None
        sas_money.is_waiting_for_para_yukle = False
        
        # Test transfer with corrected function
        print("Attempting $5.00 AFT transfer with corrected format...")
        transfer_result = sas_money.komut_para_yukle(
            doincreasetransactionid=1,
            transfertype=0,  # Cashable
            customerbalance=5.00,  # $5.00
            customerpromo=0.00,
            transactionid=0,  # Will be auto-generated
            assetnumber=asset_number,
            registrationkey=registration_key
        )
        
        print(f"Transfer initiated with transaction ID: {transfer_result}")
        
        if transfer_result:
            # Step 4: Monitor transfer status
            print("\n" + "─" * 60)
            print("⏳ STEP 4: Monitor transfer completion")
            print("─" * 60)
            
            success = False
            for i in range(15):  # Wait up to 15 seconds
                time.sleep(1)
                print(f"Monitoring... {i+1}/15")
                
                # Check transfer status
                if hasattr(sas_money, 'global_para_yukleme_transfer_status'):
                    status = sas_money.global_para_yukleme_transfer_status
                    if status:
                        print(f"Transfer status: {status}")
                        
                        if status == "00":  # Success
                            print("✅ TRANSFER SUCCESSFUL!")
                            success = True
                            break
                        elif status in ["40", "C0"]:  # Pending
                            print("⏳ Transfer pending...")
                            continue
                        elif status in ["80", "81", "82", "83", "84", "87", "FF"]:  # Failed
                            print(f"❌ Transfer failed with status: {status}")
                            break
                
                # Also check via API
                if i % 3 == 0:  # Every 3 seconds
                    current_status = get_machine_status_via_api()
                    if current_status:
                        print(f"API Status check: Lock={current_status.get('lock_status')}, AFT={current_status.get('aft_status')}")
            
            # Step 5: Final balance check
            print("\n" + "─" * 60)
            print("📊 STEP 5: Final balance and status check")
            print("─" * 60)
            
            # Query balance to see if transfer worked
            sas_money.komut_bakiye_sorgulama("corrected_test", False, "post_transfer")
            time.sleep(2)
            
            print(f"Final balance: Cashable=${sas_money.yanit_bakiye_tutar}")
            print(f"Restricted: ${sas_money.yanit_restricted_amount}")
            print(f"Non-restricted: ${sas_money.yanit_nonrestricted_amount}")
            
            # Final status via API
            final_status = get_machine_status_via_api()
            print_machine_status(final_status, "Final Status")
            
            # Results analysis
            print("\n" + "─" * 60)
            print("📋 RESULTS ANALYSIS")
            print("─" * 60)
            
            if success:
                print("🎉 SUCCESS: Corrected AFT transfer completed successfully!")
                print("✅ The command format corrections worked")
                print("✅ Machine accepted and processed the transfer")
                
                # Check if balance increased
                if hasattr(sas_money, 'yanit_bakiye_tutar') and sas_money.yanit_bakiye_tutar > 0:
                    print(f"✅ Balance increased to ${sas_money.yanit_bakiye_tutar}")
                else:
                    print("⚠️  Balance not updated - may need additional time")
                    
                return True
            else:
                print("❌ FAILED: Transfer did not complete successfully")
                print("🔍 Possible issues:")
                print("   - Machine configuration problems")
                print("   - AFT registration issues")
                print("   - Machine hardware conditions")
                print("   - Additional command format requirements")
                return False
        else:
            print("❌ FAILED: Could not initiate transfer")
            return False
        
    except Exception as e:
        print(f"❌ Error during corrected AFT test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            if 'sas_comm' in locals():
                sas_comm.close()
                print("🔧 SAS communication closed")
        except:
            pass

def main():
    """Main test function"""
    print("=" * 80)
    print("🔧 CORRECTED AFT TRANSFER VERIFICATION")
    print("=" * 80)
    print("Testing AFT transfer with corrections based on original working code:")
    print("  ✅ Proper command length calculation")
    print("  ✅ Exact BCD formatting")
    print("  ✅ Correct transaction ID conversion")
    print("  ✅ Proper CRC calculation with byte reversal")
    print("  ✅ Exact command structure from original")
    print("=" * 80)
    
    # Check initial machine status
    print("\n🔍 Initial Machine Status Check")
    status = get_machine_status_via_api()
    print_machine_status(status, "Current Status")
    
    # Run the corrected transfer test
    print("\n🎯 Running Corrected AFT Transfer Test")
    success = test_corrected_aft_transfer()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
    
    if success:
        print("🎉 OVERALL RESULT: CORRECTED AFT TRANSFER SUCCESSFUL!")
        print("✅ The command format corrections resolved the issue")
        print("✅ Machine is working correctly with proper commands")
        print("💡 RECOMMENDATION: Use the corrected AFT transfer function")
    else:
        print("❌ OVERALL RESULT: Transfer still not working")
        print("🔍 Further investigation needed:")
        print("   - Check machine hardware conditions")
        print("   - Verify AFT configuration")
        print("   - Review SAS communication settings")
        print("   - Check for additional protocol requirements")

if __name__ == "__main__":
    main() 