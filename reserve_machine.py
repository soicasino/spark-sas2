#!/usr/bin/env python3
"""
Reserve Machine Script
This script reserves a gaming machine, preventing other systems from accessing it.
Useful for testing reservation/unreservation cycles and understanding machine control.
"""

import asyncio
import time
import threading
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager

class MachineReserver:
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

async def reserve_machine():
    """Reserve the gaming machine and test reservation status"""
    
    print("=== Machine Reservation Tool ===")
    print("This tool reserves a gaming machine for exclusive access")
    
    reserver = MachineReserver()
    
    # Initialize components
    config = ConfigManager()
    port = "/dev/ttyUSB1"  # Linux USB serial port
    print(f"Using port: {port}")
    
    # Create communicator
    communicator = SASCommunicator(port, config)
    money = SasMoney(config, communicator)
    
    # Set up reserver
    reserver.communicator = communicator
    
    try:
        # Open SAS port
        print("Opening SAS port...")
        if communicator.open_port():
            print("✅ SAS port opened successfully")
        else:
            print("❌ Failed to open SAS port")
            return
        
        # Start background polling to receive responses
        reserver.start_polling()
        
        # Wait for initial communication to stabilize
        print("Waiting for initial communication to stabilize...")
        await asyncio.sleep(3)
        
        # Step 1: Check initial machine status
        print("\n=== Step 1: Check Initial Machine Status ===")
        balance_result = money.komut_bakiye_sorgulama("reserve_check", False, "initial_status")
        balance_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received:
            print("✅ Initial status query successful")
            lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            print(f"🔒 Current Lock Status: {lock_status}")
            print(f"🏭 Current AFT Status: {aft_status}")
            
            if lock_status == "00":
                print("✅ Machine is currently unlocked and available")
                print("💡 Proceeding with reservation...")
            elif lock_status == "FF":
                print("⚠️  Machine already shows all locks (may already be reserved)")
                print("💡 Attempting reservation anyway...")
            else:
                print(f"⚠️  Machine has partial locks: {lock_status}")
                print("💡 Attempting reservation...")
        else:
            print("⚠️  Initial status query failed - continuing anyway")
        
        # Step 2: AFT Registration (may be required for some reservation commands)
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
        
        # Step 3: Reserve Machine (MAIN STEP)
        print("\n=== Step 3: Reserve Machine ===")
        print("🔒 Attempting to reserve machine...")
        
        reservation_result = money.komut_reserve_machine()
        print(f"Machine reservation result: {reservation_result}")
        await asyncio.sleep(3)
        
        # Step 4: Verify Machine is Reserved
        print("\n=== Step 4: Verify Reservation Status ===")
        verify_balance = money.komut_bakiye_sorgulama("reserve_verify", False, "post_reserve_status")
        verify_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if verify_received:
            reserved_lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
            reserved_aft_status = getattr(communicator, 'last_aft_status', 'Unknown')
            
            print(f"📊 Post-Reservation Status:")
            print(f"   Lock Status: {reserved_lock_status}")
            print(f"   AFT Status: {reserved_aft_status}")
            print(f"   Balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
            
            # Analyze results
            if reserved_lock_status == "FF":
                print("❌ UNEXPECTED: Machine shows FF (not locked) - reservation may have failed")
                print("🎯 RESULT: Machine should now reject AFT transfers from other systems")
            elif reserved_lock_status != "00":
                print(f"⚠️  PARTIAL: Machine shows some locks ({reserved_lock_status}) - may be partially reserved")
                print("🎯 RESULT: Some restrictions applied")
            elif reserved_lock_status == "00":
                print("❌ RESERVATION MAY HAVE FAILED: Machine still shows unlocked status")
                print("🔍 POSSIBLE CAUSES:")
                print("   - Machine doesn't support software reservation")
                print("   - Different SAS command needed for this machine model")
                print("   - Reservation requires additional parameters")
            else:
                print(f"❓ UNKNOWN STATUS: {reserved_lock_status}")
        else:
            print("⚠️  Could not verify reservation status")
        
        # Step 5: Test AFT Transfer (should fail if properly reserved)
        print("\n=== Step 5: Test AFT Transfer (Should Fail) ===")
        try:
            print("💰 Testing $1.00 AFT transfer (expecting failure)...")
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
                print("⚠️  UNEXPECTED: AFT transfer succeeded despite reservation")
                print("🔍 ANALYSIS: Machine may not be properly reserved")
            elif transfer_success is False:
                print("✅ EXPECTED: AFT transfer failed (machine properly reserved)")
                print("🎯 CONCLUSION: Machine reservation is working correctly")
            else:
                print("⏳ AFT transfer timed out")
                print("🔍 ANALYSIS: Machine may be rejecting due to reservation")
                
        except Exception as e:
            print(f"Test transfer error: {e}")
            print("🔍 This may be expected if machine is properly reserved")
        
        # Step 6: Demonstrate Reservation Clearing
        print("\n=== Step 6: Demonstrate Reservation Clearing ===")
        user_input = input("Do you want to clear the reservation now? (y/n): ").lower().strip()
        
        if user_input == 'y':
            print("🔧 Clearing machine reservation...")
            clear_result = money.komut_clear_reservation_sequence()
            print(f"Reservation clearing result: {clear_result}")
            await asyncio.sleep(3)
            
            # Verify clearing
            final_balance = money.komut_bakiye_sorgulama("final_verify", False, "post_clear_status")
            final_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
            
            if final_received:
                final_lock_status = getattr(communicator, 'last_game_lock_status', 'Unknown')
                print(f"📊 Final Status After Clearing:")
                print(f"   Lock Status: {final_lock_status}")
                
                if final_lock_status == "00":
                    print("✅ SUCCESS: Machine reservation cleared")
                elif final_lock_status != "FF":
                    print(f"⚠️  PARTIAL: Lock status improved to {final_lock_status}")
                else:
                    print("❌ Machine still appears reserved")
        else:
            print("ℹ️  Leaving machine in reserved state")
            print("💡 Use clear_machine_reservation.py to clear later")
        
        # Final summary
        print("\n=== FINAL SUMMARY ===")
        if verify_received:
            if reserved_lock_status == "FF":
                print("🎉 SUCCESS: Machine successfully reserved")
                print("🔒 RESULT: Machine is locked and should reject external AFT transfers")
            elif reserved_lock_status != "00":
                print("⚠️  PARTIAL: Machine shows some reservation/lock status")
            else:
                print("❌ FAILED: Machine reservation may not have worked")
                print("💡 TROUBLESHOOTING:")
                print("   1. Check if machine supports software reservation")
                print("   2. Try different SAS reservation commands")
                print("   3. Check machine documentation for reservation procedure")
        
        # Give some time for any final responses
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Error in machine reservation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nCleaning up...")
        reserver.stop_polling()
        communicator.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    asyncio.run(reserve_machine()) 