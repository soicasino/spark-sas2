#!/usr/bin/env python3
"""
Clear Machine Reservation Script
This script specifically addresses machines that are "reserved" and won't accept AFT transfers.
"""

import asyncio
import time
import threading
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager

class ReservationClearer:
    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.communicator = None
        
    def start_polling(self):
        """Start background polling thread"""
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        print("✅ Background polling started")
        
    def stop_polling(self):
        """Stop background polling"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1)
        print("✅ Background polling stopped")
        
    def _poll_loop(self):
        """Background polling loop to receive SAS responses"""
        while self.running:
            try:
                if self.communicator and self.communicator.is_port_open:
                    # Get any incoming data
                    data = self.communicator.get_data_from_sas_port()
                    if data:
                        print(f"RX: {data}")
                        # Process the received data
                        self.communicator.handle_received_sas_command(data)
                    
                    # Send periodic general poll (alternating 80/81)
                    self.communicator.send_general_poll()
                    
                time.sleep(0.1)  # Poll every 100ms
            except Exception as e:
                print(f"Error in polling loop: {e}")
                time.sleep(0.5)

async def clear_reservation():
    """Clear machine reservation and enable AFT transfers"""
    
    print("=== Machine Reservation Clearing Tool ===")
    print("This tool clears 'reserved' status from gaming machines")
    
    clearer = ReservationClearer()
    
    # Initialize components
    config = ConfigManager()
    port = "/dev/ttyUSB1"  # Linux USB serial port
    print(f"Using port: {port}")
    
    # Create communicator
    communicator = SASCommunicator(port, config)
    money = SasMoney(config, communicator)
    
    # Set up clearer
    clearer.communicator = communicator
    
    try:
        # Open SAS port
        print("Opening SAS port...")
        if communicator.open_port():
            print("✅ SAS port opened successfully")
        else:
            print("❌ Failed to open SAS port")
            return
        
        # Start background polling to receive responses
        clearer.start_polling()
        
        # Wait for initial communication to stabilize
        print("Waiting for initial communication to stabilize...")
        await asyncio.sleep(3)
        
        # Step 1: Check initial machine status
        print("\n=== Step 1: Check Initial Machine Status ===")
        balance_result = money.komut_bakiye_sorgulama("reservation_check", False, "initial_status")
        balance_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received:
            print("✅ Initial status query successful")
            lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            print(f"🔒 Current Lock Status: {lock_status}")
            print(f"🏭 Current AFT Status: {aft_status}")
            
            if lock_status == "FF":
                print("✅ DIAGNOSIS: Machine shows FF (not locked - normal operation)")
                print("💡 SOLUTION: Attempting to clear reservation...")
            elif lock_status == "00":
                print("✅ Machine appears to be unlocked already")
                print("ℹ️  Continuing with verification...")
            else:
                print(f"⚠️  Machine has partial locks: {lock_status}")
                print("💡 Attempting to clear anyway...")
        else:
            print("⚠️  Initial status query failed - continuing anyway")
        
        # Step 2: AFT Registration (required before clearing reservation)
        print("\n=== Step 2: AFT Registration ===")
        asset_number = "0000006C"  # Known asset number
        registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex key
        pos_id = "POS1"  # POS identifier
        
        try:
            reg_result = money.komut_aft_registration(asset_number, registration_key, pos_id)
            print(f"AFT Registration result: {reg_result}")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"AFT Registration failed: {e}")
        
        # Step 3: Clear Machine Reservation (MAIN STEP)
        print("\n=== Step 3: Clear Machine Reservation ===")
        print("🔧 Starting comprehensive reservation clearing sequence...")
        
        reservation_result = money.komut_clear_reservation_sequence()
        print(f"Reservation clearing result: {reservation_result}")
        await asyncio.sleep(3)
        
        # Step 4: Verify Reservation Cleared
        print("\n=== Step 4: Verify Reservation Status ===")
        verify_balance = money.komut_bakiye_sorgulama("reservation_verify", False, "post_clear_status")
        verify_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if verify_received:
            final_lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            final_aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            
            print(f"📊 Post-Clear Status:")
            print(f"   Lock Status: {final_lock_status}")
            print(f"   AFT Status: {final_aft_status}")
            print(f"   Balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
            
            # Analyze results
            if final_lock_status == "00":
                print("✅ SUCCESS: Machine reservation cleared! Machine is now unlocked.")
                print("🎯 RESULT: AFT transfers should now work normally")
            elif final_lock_status != "FF":
                print(f"⚠️  PARTIAL SUCCESS: Lock status improved from FF to {final_lock_status}")
                print("🎯 RESULT: Some restrictions may remain, but AFT may work")
            elif final_lock_status == "FF":
                print("❌ RESERVATION STILL ACTIVE: Machine still shows all locks")
                print("🔍 POSSIBLE CAUSES:")
                print("   - Machine requires physical key/switch to clear reservation")
                print("   - Different SAS command needed for this machine model")
                print("   - Machine is in permanent test/simulation mode")
                print("   - Hardware-level reservation that can't be cleared via SAS")
            else:
                print(f"❓ UNKNOWN STATUS: {final_lock_status}")
        else:
            print("⚠️  Could not verify final status")
        
        # Step 5: Test AFT Transfer (if machine appears ready)
        if verify_received and final_lock_status in ["00", "01", "02", "04", "08"]:  # Any improvement from FF
            print("\n=== Step 5: Test AFT Transfer ===")
            try:
                print("💰 Testing $1.00 AFT transfer...")
                transfer_result = money.komut_para_yukle(
                    doincreasetransactionid=True,
                    transfertype=0,  # Non-restricted
                    customerbalance=1.00,  # $1.00
                    customerpromo=0.00,
                    transactionid=0,
                    assetnumber=asset_number,
                    registrationkey=registration_key
                )
                print(f"Test transfer initiated: {transfer_result}")
                
                # Wait for transfer completion
                transfer_success = await money.wait_for_para_yukle_completion(timeout=10)
                
                if transfer_success is True:
                    print("✅ AFT TRANSFER SUCCESSFUL!")
                    print("🎯 CONCLUSION: Machine reservation successfully cleared")
                elif transfer_success is False:
                    print("❌ AFT transfer failed")
                    print("⚠️  Machine may still have restrictions")
                else:
                    print("⏳ AFT transfer timed out")
                    print("⚠️  Machine may be processing or have timing issues")
                    
            except Exception as e:
                print(f"Test transfer error: {e}")
        else:
            print("\n=== Step 5: Skipped AFT Test ===")
            print("Machine still appears locked - skipping transfer test")
        
        # Final summary
        print("\n=== FINAL SUMMARY ===")
        if verify_received:
            if final_lock_status == "00":
                print("🎉 SUCCESS: Machine reservation cleared and ready for AFT transfers")
            elif final_lock_status != "FF":
                print("⚠️  PARTIAL: Some improvement achieved, AFT may work with restrictions")
            else:
                print("❌ FAILED: Machine reservation could not be cleared via SAS commands")
                print("💡 NEXT STEPS:")
                print("   1. Check for physical reservation key/switch on machine")
                print("   2. Contact machine manufacturer for reservation clearing procedure")
                print("   3. Check if machine requires different SAS commands")
                print("   4. Verify machine is not in permanent test mode")
        
        # Give some time for any final responses
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Error in reservation clearing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nCleaning up...")
        clearer.stop_polling()
        communicator.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    asyncio.run(clear_reservation()) 