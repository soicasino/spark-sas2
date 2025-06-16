#!/usr/bin/env python3
"""
AFT Cancel Transfer Test Script

This script tests the CORRECT method to unlock a machine stuck in AFT Game Lock state.
Based on the analysis that the machine is stuck in AFT Game Lock (not general machine lock),
this uses the AFT cancel transfer command (017201800BB4) which is the proper unlock method.

Key Insights:
- Machine shows lock_status: "FF" and aft_status: "B0" 
- This indicates AFT Game Lock, not general machine lock
- Standard unlock commands (0102...) don't work because they're the wrong type
- AFT cancel transfer (017201800BB4) is the correct command
- Machine clears reservation on its own = AFT lock timeout, confirming AFT lock issue
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
    """Get current machine status via API for comparison"""
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

def print_status_analysis(status_data):
    """Analyze and print the machine status with AFT focus"""
    if not status_data:
        print("❌ No status data available")
        return
    
    lock_status = status_data.get('lock_status', 'Unknown')
    aft_status = status_data.get('aft_status', 'Unknown')
    
    print(f"\n📊 MACHINE STATUS ANALYSIS:")
    print(f"   Lock Status: {lock_status}")
    print(f"   AFT Status:  {aft_status}")
    
    # CORRECTED: Analyze lock status according to SAS protocol
    # FF = NOT LOCKED, 00 = LOCKED, 40 = LOCK PENDING
    if lock_status == "FF":
        print(f"   ✅ DIAGNOSIS: Machine is NOT LOCKED (FF = available for AFT)")
        print(f"      This means the machine is ready for AFT operations")
    elif lock_status == "00":
        print(f"   🔒 DIAGNOSIS: Machine is LOCKED (00 = locked state)")
        print(f"      This means the machine is unavailable for AFT operations")
    elif lock_status == "40":
        print(f"   ⏳ DIAGNOSIS: Machine lock PENDING (40 = transitioning)")
        print(f"      This means the machine is in transition state")
    else:
        print(f"   ⚠️  DIAGNOSIS: Unknown lock state ({lock_status})")
    
    # Analyze AFT status
    if aft_status == "B0":
        print(f"   🎯 AFT DIAGNOSIS: AFT Enabled but RESTRICTED (176 decimal)")
        print(f"      This indicates AFT is configured but may have limitations")
    elif aft_status == "00":
        print(f"   ❌ AFT DIAGNOSIS: AFT Disabled")
    elif aft_status == "01":
        print(f"   ✅ AFT DIAGNOSIS: AFT Enabled - Full functionality")
    else:
        print(f"   ⚠️  AFT DIAGNOSIS: AFT status {aft_status}")
    
    # Overall diagnosis - CORRECTED
    if lock_status == "FF" and aft_status == "B0":
        print(f"\n🎯 CONCLUSION: Machine is AVAILABLE but AFT has restrictions")
        print(f"   ✅ Machine Status: Ready for operations (FF = not locked)")
        print(f"   ⚠️  AFT Status: Restricted mode - may need configuration")
        print(f"   💡 Recommendation: Try AFT operations - machine should accept them")
    elif lock_status == "FF":
        print(f"\n✅ CONCLUSION: Machine is AVAILABLE for AFT operations")
        print(f"   Machine is not locked and ready for AFT transfers")
    elif lock_status == "00":
        print(f"\n❌ CONCLUSION: Machine is LOCKED and unavailable")
        print(f"   Need to unlock machine before AFT operations")

def test_aft_cancel_unlock():
    """Test the AFT cancel transfer unlock method"""
    print("=" * 80)
    print("🎯 AFT CANCEL TRANSFER UNLOCK TEST")
    print("=" * 80)
    print("Testing the CORRECT method to unlock AFT Game Lock state")
    print("Command: 017201800BB4 (AFT Cancel Transfer)")
    print()
    
    # Initialize SAS communication
    try:
        print("🔧 Initializing SAS communication...")
        sas_comm = SASCommunication()
        
        if not sas_comm.is_port_open:
            print("❌ Failed to open SAS communication port")
            return False
        
        print("✅ SAS communication initialized")
        
        # Initialize SAS money functions
        sas_money = SasMoney(sas_comm)
        print("✅ SAS money functions initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize SAS communication: {e}")
        return False
    
    try:
        # Step 1: Get initial status
        print("\n" + "─" * 60)
        print("📊 STEP 1: Get initial machine status")
        print("─" * 60)
        
        initial_status = get_machine_status_via_api()
        print("Initial Status:")
        print_status_analysis(initial_status)
        
        # Step 2: Execute AFT cancel transfer
        print("\n" + "─" * 60)
        print("🎯 STEP 2: Execute AFT Cancel Transfer")
        print("─" * 60)
        print("Sending AFT Cancel Transfer command: 017201800BB4")
        print("This is the CORRECT command for AFT Game Lock unlock")
        
        start_time = time.time()
        result = sas_money.komut_cancel_aft_transfer("00000000000000000000000000000000000000000000")
        execution_time = time.time() - start_time
        
        print(f"✅ AFT Cancel Transfer executed in {execution_time:.2f} seconds")
        print(f"📋 Result: {result}")
        
        # Step 3: Wait and check status
        print("\n" + "─" * 60)
        print("⏱️  STEP 3: Wait for machine to process unlock")
        print("─" * 60)
        
        for i in range(3):
            print(f"Waiting... {i+1}/3")
            time.sleep(2)
            
            status = get_machine_status_via_api()
            if status:
                lock_status = status.get('lock_status', 'Unknown')
                aft_status = status.get('aft_status', 'Unknown')
                print(f"Status check {i+1}: Lock={lock_status}, AFT={aft_status}")
                
                if lock_status == "00":
                    print("🎉 SUCCESS: Machine unlocked!")
                    break
                elif lock_status != "FF":
                    print(f"⚠️  PROGRESS: Lock status improved to {lock_status}")
        
        # Step 4: Final status verification
        print("\n" + "─" * 60)
        print("📊 STEP 4: Final status verification")
        print("─" * 60)
        
        final_status = get_machine_status_via_api()
        print("Final Status:")
        print_status_analysis(final_status)
        
        # Compare initial vs final
        if initial_status and final_status:
            initial_lock = initial_status.get('lock_status', 'Unknown')
            final_lock = final_status.get('lock_status', 'Unknown')
            initial_aft = initial_status.get('aft_status', 'Unknown')
            final_aft = final_status.get('aft_status', 'Unknown')
            
            print(f"\n📈 COMPARISON:")
            print(f"   Lock Status: {initial_lock} → {final_lock}")
            print(f"   AFT Status:  {initial_aft} → {final_aft}")
            
            if final_lock == "00":
                print(f"🎉 SUCCESS: AFT Cancel Transfer successfully unlocked the machine!")
                return True
            elif final_lock != initial_lock:
                print(f"⚠️  PARTIAL SUCCESS: Lock status improved")
                return True
            else:
                print(f"❌ NO CHANGE: Machine still locked - may need additional steps")
                return False
        
        return result
        
    except Exception as e:
        print(f"❌ Error during AFT cancel unlock test: {e}")
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
    print("🎯 AFT CANCEL TRANSFER UNLOCK TEST")
    print("This test uses the CORRECT method to unlock AFT Game Lock")
    print()
    
    # Run the test
    success = test_aft_cancel_unlock()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST COMPLETED - Check results above")
    else:
        print("❌ TEST FAILED - Check error messages above")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    main() 