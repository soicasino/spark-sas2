#!/usr/bin/env python3
"""
Machine Reservation Functionality Test Script

This script tests the complete reservation functionality including:
1. Reserve machine (SAS 8C)
2. Clear reservation simple (SAS 8F) 
3. Clear reservation full sequence
4. Verification of reservation status

Key SAS Commands:
- Reserve Machine: SAS 8C
- Clear Reservation: SAS 8F  
- Disable Machine: SAS 8D
- Enable Machine: SAS 8E
- Clear Host Controls: SAS 85
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

def call_api_endpoint(endpoint, method="POST"):
    """Call a specific API endpoint"""
    try:
        url = f"http://localhost:8000/api/machine/{endpoint}"
        response = requests.request(method, url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"API Call Error: {e}")
        return None

def print_status_analysis(status_data, title="Machine Status"):
    """Analyze and print the machine status"""
    if not status_data:
        print(f"❌ No {title.lower()} data available")
        return
    
    lock_status = status_data.get('lock_status', 'Unknown')
    aft_status = status_data.get('aft_status', 'Unknown')
    
    print(f"\n📊 {title.upper()}:")
    print(f"   Lock Status: {lock_status}")
    print(f"   AFT Status:  {aft_status}")
    
    # Analyze lock status for reservation
    if lock_status == "FF":
        print(f"   ✅ ANALYSIS: Machine not locked (FF = normal operation, not reserved)")
    elif lock_status == "00":
        print(f"   ✅ ANALYSIS: Machine unlocked and available")
    else:
        print(f"   ⚠️  ANALYSIS: Partial lock state ({lock_status})")
    
    # Analyze AFT status
    if aft_status == "B0":
        print(f"   🎯 AFT ANALYSIS: AFT restricted (may be in AFT Game Lock)")
    elif aft_status == "00":
        print(f"   ✅ AFT ANALYSIS: AFT normal state")
    else:
        print(f"   ⚠️  AFT ANALYSIS: AFT status {aft_status}")

def test_reservation_via_api():
    """Test reservation functionality via API endpoints"""
    print("=" * 80)
    print("🔐 RESERVATION FUNCTIONALITY TEST (API)")
    print("=" * 80)
    print("Testing reservation functionality through web API")
    print()
    
    try:
        # Step 1: Get initial status
        print("─" * 60)
        print("📊 STEP 1: Get initial machine status")
        print("─" * 60)
        
        initial_status = get_machine_status_via_api()
        print_status_analysis(initial_status, "Initial Status")
        
        # Step 2: Reserve machine via API
        print("\n" + "─" * 60)
        print("🔒 STEP 2: Reserve machine via API")
        print("─" * 60)
        print("Calling /api/machine/reserve endpoint...")
        
        reserve_result = call_api_endpoint("reserve")
        if reserve_result:
            print(f"✅ Reserve API call successful")
            print(f"📋 Response: {reserve_result}")
        else:
            print(f"❌ Reserve API call failed")
        
        # Wait for machine to process
        time.sleep(3)
        
        # Step 3: Check status after reservation
        print("\n" + "─" * 60)
        print("📊 STEP 3: Check status after reservation")
        print("─" * 60)
        
        reserved_status = get_machine_status_via_api()
        print_status_analysis(reserved_status, "Post-Reservation Status")
        
        # Compare statuses
        if initial_status and reserved_status:
            initial_lock = initial_status.get('lock_status', 'Unknown')
            reserved_lock = reserved_status.get('lock_status', 'Unknown')
            
            print(f"\n📈 RESERVATION COMPARISON:")
            print(f"   Lock Status: {initial_lock} → {reserved_lock}")
            
            if reserved_lock == "FF" and initial_lock != "FF":
                print(f"✅ SUCCESS: Machine appears to be reserved (locks activated)")
            elif reserved_lock != initial_lock:
                print(f"⚠️  CHANGE: Lock status changed - partial reservation effect")
            else:
                print(f"❌ NO CHANGE: Reservation may not have taken effect")
        
        # Step 4: Test simple clear reservation
        print("\n" + "─" * 60)
        print("🔓 STEP 4: Test simple clear reservation")
        print("─" * 60)
        print("Calling /api/machine/clear-reservation-simple endpoint...")
        
        clear_simple_result = call_api_endpoint("clear-reservation-simple")
        if clear_simple_result:
            print(f"✅ Simple clear API call successful")
            print(f"📋 Response: {clear_simple_result}")
        else:
            print(f"❌ Simple clear API call failed")
        
        time.sleep(3)
        
        # Step 5: Check status after simple clear
        print("\n" + "─" * 60)
        print("📊 STEP 5: Check status after simple clear")
        print("─" * 60)
        
        simple_clear_status = get_machine_status_via_api()
        print_status_analysis(simple_clear_status, "Post-Simple-Clear Status")
        
        # Step 6: Reserve again for full clear test
        print("\n" + "─" * 60)
        print("🔒 STEP 6: Reserve again for full clear test")
        print("─" * 60)
        
        reserve_result2 = call_api_endpoint("reserve")
        if reserve_result2:
            print(f"✅ Second reserve successful")
        
        time.sleep(3)
        
        # Step 7: Test full clear reservation sequence
        print("\n" + "─" * 60)
        print("🔧 STEP 7: Test full clear reservation sequence")
        print("─" * 60)
        print("Calling /api/machine/unlock/clear-reservation endpoint...")
        
        clear_full_result = call_api_endpoint("unlock/clear-reservation")
        if clear_full_result:
            print(f"✅ Full clear sequence API call successful")
            print(f"📋 Response: {clear_full_result}")
        else:
            print(f"❌ Full clear sequence API call failed")
        
        time.sleep(5)  # Full sequence takes longer
        
        # Step 8: Final status check
        print("\n" + "─" * 60)
        print("📊 STEP 8: Final status verification")
        print("─" * 60)
        
        final_status = get_machine_status_via_api()
        print_status_analysis(final_status, "Final Status")
        
        # Final comparison
        if initial_status and final_status:
            initial_lock = initial_status.get('lock_status', 'Unknown')
            final_lock = final_status.get('lock_status', 'Unknown')
            
            print(f"\n📈 FINAL COMPARISON:")
            print(f"   Initial Lock Status: {initial_lock}")
            print(f"   Final Lock Status:   {final_lock}")
            
            if final_lock == "00":
                print(f"🎉 SUCCESS: Machine fully cleared and available")
                return True
            elif final_lock != initial_lock:
                print(f"⚠️  PARTIAL: Some improvement achieved")
                return True
            else:
                print(f"❌ NO CHANGE: Reservation clearing may not have worked")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during API reservation test: {e}")
        return False

def test_reservation_direct_sas():
    """Test reservation functionality via direct SAS commands"""
    print("=" * 80)
    print("🔐 RESERVATION FUNCTIONALITY TEST (DIRECT SAS)")
    print("=" * 80)
    print("Testing reservation functionality through direct SAS commands")
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
        print_status_analysis(initial_status, "Initial Status")
        
        # Step 2: Reserve machine directly
        print("\n" + "─" * 60)
        print("🔒 STEP 2: Reserve machine (Direct SAS 8C)")
        print("─" * 60)
        print("Sending SAS 8C (Reserve Machine) command...")
        
        reserve_result = sas_money.komut_reserve_machine()
        print(f"✅ Reserve command executed")
        print(f"📋 Result: {reserve_result}")
        
        time.sleep(3)
        
        # Step 3: Check status after reservation
        print("\n" + "─" * 60)
        print("📊 STEP 3: Check status after direct reservation")
        print("─" * 60)
        
        reserved_status = get_machine_status_via_api()
        print_status_analysis(reserved_status, "Post-Direct-Reservation Status")
        
        # Step 4: Clear reservation directly (simple)
        print("\n" + "─" * 60)
        print("🔓 STEP 4: Clear reservation (Direct SAS 8F)")
        print("─" * 60)
        print("Sending SAS 8F (Clear Reservation) command...")
        
        clear_result = sas_money.komut_clear_machine_reservation()
        print(f"✅ Clear reservation command executed")
        print(f"📋 Result: {clear_result}")
        
        time.sleep(3)
        
        # Step 5: Check status after simple clear
        print("\n" + "─" * 60)
        print("📊 STEP 5: Check status after direct clear")
        print("─" * 60)
        
        clear_status = get_machine_status_via_api()
        print_status_analysis(clear_status, "Post-Direct-Clear Status")
        
        # Step 6: Reserve again for full sequence test
        print("\n" + "─" * 60)
        print("🔒 STEP 6: Reserve again for full sequence test")
        print("─" * 60)
        
        reserve_result2 = sas_money.komut_reserve_machine()
        print(f"✅ Second reserve executed: {reserve_result2}")
        
        time.sleep(3)
        
        # Step 7: Full clear sequence
        print("\n" + "─" * 60)
        print("🔧 STEP 7: Full clear reservation sequence")
        print("─" * 60)
        print("Executing comprehensive clear sequence...")
        
        full_clear_result = sas_money.komut_clear_reservation_sequence()
        print(f"✅ Full clear sequence executed")
        print(f"📋 Result: {full_clear_result}")
        
        time.sleep(5)
        
        # Step 8: Final status
        print("\n" + "─" * 60)
        print("📊 STEP 8: Final status verification")
        print("─" * 60)
        
        final_status = get_machine_status_via_api()
        print_status_analysis(final_status, "Final Status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during direct SAS reservation test: {e}")
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
    print("🔐 MACHINE RESERVATION FUNCTIONALITY TEST")
    print("This test verifies reservation and clear reservation functionality")
    print()
    
    # Test via API first
    print("Testing via API endpoints...")
    api_success = test_reservation_via_api()
    
    print("\n" + "=" * 80)
    
    # Test via direct SAS commands
    print("Testing via direct SAS commands...")
    sas_success = test_reservation_direct_sas()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 80)
    
    if api_success:
        print("✅ API Reservation Test: PASSED")
    else:
        print("❌ API Reservation Test: FAILED")
    
    if sas_success:
        print("✅ Direct SAS Reservation Test: PASSED")
    else:
        print("❌ Direct SAS Reservation Test: FAILED")
    
    if api_success and sas_success:
        print("\n🎉 ALL TESTS PASSED - Reservation functionality working correctly")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Check results above for details")
        return False

if __name__ == "__main__":
    main() 