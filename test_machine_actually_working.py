#!/usr/bin/env python3
"""
Machine Status Verification Test

This script tests the CORRECTED understanding of SAS lock status values:
- FF = NOT LOCKED (machine available for AFT)
- 40 = LOCK PENDING 
- 00 = LOCKED (machine unavailable)

Based on SAS Protocol documentation, if machine shows lock_status: "FF" and aft_status: "B0",
this means the machine is AVAILABLE and AFT is enabled but restricted.
The machine should accept AFT transfers without needing any unlock commands.
"""

import sys
import os
import time
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communication import SASCommunication
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

def print_corrected_status_analysis(status_data):
    """Analyze machine status with CORRECTED SAS protocol understanding"""
    if not status_data:
        print("❌ No status data available")
        return
    
    lock_status = status_data.get('lock_status', 'Unknown')
    aft_status = status_data.get('aft_status', 'Unknown')
    is_locked = status_data.get('is_locked', 'Unknown')
    
    print(f"\n📊 CORRECTED MACHINE STATUS ANALYSIS:")
    print(f"   Lock Status: {lock_status}")
    print(f"   AFT Status:  {aft_status}")
    print(f"   Is Locked:   {is_locked}")
    
    # CORRECTED interpretation based on SAS protocol
    if lock_status == "FF":
        print(f"   ✅ MACHINE STATUS: NOT LOCKED (FF = available)")
        print(f"      🎯 This means the machine is READY for AFT operations")
        print(f"      🚫 NO UNLOCK NEEDED - machine is already available")
    elif lock_status == "00":
        print(f"   🔒 MACHINE STATUS: LOCKED (00 = unavailable)")
        print(f"      ⚠️  This means the machine needs to be unlocked")
    elif lock_status == "40":
        print(f"   ⏳ MACHINE STATUS: LOCK PENDING (40 = transitioning)")
        print(f"      ⚠️  Machine is in transition state")
    else:
        print(f"   ❓ MACHINE STATUS: Unknown ({lock_status})")
    
    # AFT Status analysis
    if aft_status == "B0":
        print(f"   🎯 AFT STATUS: Enabled but Restricted (B0)")
        print(f"      💡 This is normal - AFT is configured and should work")
        print(f"      📝 B0 = AFT enabled with some restrictions (normal operation)")
    elif aft_status == "01":
        print(f"   ✅ AFT STATUS: Fully Enabled (01)")
    elif aft_status == "00":
        print(f"   ❌ AFT STATUS: Disabled (00)")
    else:
        print(f"   ❓ AFT STATUS: {aft_status}")
    
    # Overall conclusion
    if lock_status == "FF" and aft_status == "B0":
        print(f"\n🎉 FINAL CONCLUSION: MACHINE IS WORKING CORRECTLY!")
        print(f"   ✅ Machine is NOT LOCKED (ready for operations)")
        print(f"   ✅ AFT is ENABLED (restricted mode is normal)")
        print(f"   💡 RECOMMENDATION: Try AFT transfers directly - no unlock needed")
        print(f"   🚫 STOP trying unlock commands - they're unnecessary!")
        return "READY"
    elif lock_status == "FF":
        print(f"\n✅ CONCLUSION: Machine available, check AFT configuration")
        return "AVAILABLE"
    elif lock_status == "00":
        print(f"\n❌ CONCLUSION: Machine is locked and needs unlocking")
        return "LOCKED"
    else:
        print(f"\n❓ CONCLUSION: Unknown machine state")
        return "UNKNOWN"

def test_aft_transfer_directly():
    """Test AFT transfer directly without any unlock commands"""
    print("=" * 80)
    print("🎯 DIRECT AFT TRANSFER TEST")
    print("=" * 80)
    print("Testing AFT transfer WITHOUT unlock commands")
    print("Based on corrected understanding: FF = NOT LOCKED")
    print()
    
    try:
        print("🔧 Initializing SAS communication...")
        sas_comm = SASCommunication()
        
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
        # Step 1: Check current status
        print("\n" + "─" * 60)
        print("📊 STEP 1: Check current machine status")
        print("─" * 60)
        
        status = get_machine_status_via_api()
        machine_state = print_corrected_status_analysis(status)
        
        if machine_state != "READY":
            print(f"\n⚠️  Machine state is {machine_state}, not READY")
            if machine_state == "LOCKED":
                print("❌ Machine is actually locked - unlock commands may be needed")
                return False
            else:
                print("⚠️  Proceeding with caution...")
        
        # Step 2: AFT Registration (required for transfers)
        print("\n" + "─" * 60)
        print("🔧 STEP 2: AFT Registration")
        print("─" * 60)
        
        asset_number = "0000006C"  # Known asset number (108 decimal)
        registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex
        pos_id = "POS1"
        
        print(f"Registering AFT with asset number: {asset_number}")
        reg_result = sas_money.komut_aft_registration(asset_number, registration_key, pos_id)
        print(f"AFT Registration result: {reg_result}")
        time.sleep(2)
        
        # Step 3: Direct AFT Transfer Test
        print("\n" + "─" * 60)
        print("💰 STEP 3: Direct AFT Transfer Test")
        print("─" * 60)
        print("Attempting $1.00 AFT transfer WITHOUT any unlock commands")
        
        # Try a small transfer
        transfer_result = sas_money.komut_para_yukle(
            doincreasetransactionid=True,
            transfertype=0,  # Non-restricted
            customerbalance=1.00,  # $1.00
            customerpromo=0.00,
            transactionid=0,
            assetnumber=asset_number,
            registrationkey=registration_key
        )
        
        print(f"Transfer initiated: {transfer_result}")
        
        # Wait for completion
        print("⏳ Waiting for transfer completion...")
        success = False
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            print(f"Waiting... {i+1}/10")
            
            # Check if transfer completed
            if hasattr(sas_money, 'global_para_yukleme_transfer_status'):
                status = sas_money.global_para_yukleme_transfer_status
                print(f"Transfer status: {status}")
                
                if status == "00":  # Success
                    print("✅ TRANSFER SUCCESSFUL!")
                    success = True
                    break
                elif status in ["80", "FF"]:  # Failed
                    print(f"❌ Transfer failed with status: {status}")
                    break
        
        # Step 4: Check balance after transfer
        print("\n" + "─" * 60)
        print("📊 STEP 4: Check balance after transfer")
        print("─" * 60)
        
        sas_money.komut_bakiye_sorgulama("direct_test", False, "post_transfer")
        time.sleep(2)
        
        print(f"Balance: Cashable=${sas_money.yanit_bakiye_tutar}")
        print(f"Restricted: ${sas_money.yanit_restricted_amount}")
        print(f"Non-restricted: ${sas_money.yanit_nonrestricted_amount}")
        
        # Final status check
        final_status = get_machine_status_via_api()
        print("\n📊 FINAL STATUS:")
        print_corrected_status_analysis(final_status)
        
        if success:
            print("\n🎉 SUCCESS: AFT transfer worked without unlock commands!")
            print("✅ CONCLUSION: Machine was working correctly all along")
            print("🚫 RECOMMENDATION: Stop using unlock commands - they're not needed")
            return True
        else:
            print("\n❌ FAILED: AFT transfer did not complete successfully")
            print("🔍 INVESTIGATION: Check AFT configuration or machine conditions")
            return False
        
    except Exception as e:
        print(f"❌ Error during direct AFT test: {e}")
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
    print("🔍 MACHINE STATUS VERIFICATION TEST")
    print("=" * 80)
    print("Testing CORRECTED understanding of SAS lock status:")
    print("  FF = NOT LOCKED (machine available)")
    print("  00 = LOCKED (machine unavailable)")
    print("  40 = LOCK PENDING (transitioning)")
    print()
    print("If machine shows FF + B0, it should work WITHOUT unlock commands!")
    print("=" * 80)
    
    # Test 1: Check current status
    print("\n🔍 TEST 1: Current Machine Status")
    status = get_machine_status_via_api()
    machine_state = print_corrected_status_analysis(status)
    
    # Test 2: Direct AFT transfer if machine appears ready
    if machine_state == "READY":
        print("\n🎯 TEST 2: Direct AFT Transfer (No Unlock)")
        success = test_aft_transfer_directly()
        
        if success:
            print("\n🎉 OVERALL RESULT: MACHINE IS WORKING CORRECTLY!")
            print("✅ No unlock commands needed")
            print("✅ AFT transfers work as expected")
            print("🚫 Stop trying to 'fix' what isn't broken!")
        else:
            print("\n⚠️  OVERALL RESULT: AFT transfer failed")
            print("🔍 Further investigation needed")
    else:
        print(f"\n⚠️  Machine state is {machine_state} - may need attention")
        if machine_state == "LOCKED":
            print("❌ Machine is actually locked - unlock procedures may be needed")
        else:
            print("🔍 Check machine configuration and status")

if __name__ == "__main__":
    main() 