#!/usr/bin/env python3
"""
Test script to try different machine unlock methods and AFT registration.
This script attempts various approaches to unlock the machine and enable AFT transfers.
Includes background polling to receive SAS responses.
"""

import asyncio
import time
import threading
from sas_communicator import SASCommunicator
from sas_money_functions import SasMoney
from config_manager import ConfigManager

class UnlockTester:
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

async def test_machine_unlock():
    """Test different methods to unlock the machine and enable AFT"""
    
    print("=== Machine Unlock and AFT Test with Polling ===")
    
    tester = UnlockTester()
    
    # Initialize components
    config = ConfigManager()
    port = "/dev/ttyUSB1"  # Linux USB serial port
    print(f"Using port: {port}")
    
    # Create communicator
    communicator = SASCommunicator(port, config)
    money = SasMoney(config, communicator)
    
    # Set up tester
    tester.communicator = communicator
    
    try:
        # Open SAS port
        print("Opening SAS port...")
        if communicator.open_port():
            print("✅ SAS port opened successfully")
        else:
            print("❌ Failed to open SAS port")
            return
        
        # Start background polling to receive responses
        tester.start_polling()
        
        # Wait for initial communication to stabilize
        print("Waiting for initial communication to stabilize...")
        await asyncio.sleep(3)
        
        print("\n=== Initial Balance Check ===")
        # Check initial balance
        balance_result = money.komut_bakiye_sorgulama("unlock_test", False, "initial_balance")
        balance_received = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received:
            print("✅ Initial balance query successful")
        else:
            print("⚠️  Initial balance query failed")
        
        print(f"Balance received: {balance_received}")
        print(f"Current balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        print("\n=== Trying Different Unlock Methods ===")
        
        # Method 1: AFT Registration first (prerequisite for unlock)
        print("Method 1: AFT Registration")
        try:
            # Use correct method name and provide required parameters
            asset_number = "0000006C"  # Known asset number (108 decimal)
            registration_key = "1234567890ABCDEF1234567890ABCDEF12345678"  # 40-char hex key
            pos_id = "POS1"  # POS identifier
            
            reg_result = money.komut_aft_registration(asset_number, registration_key, pos_id)
            print(f"AFT Registration result: {reg_result}")
            await asyncio.sleep(3)  # Give more time for registration
        except Exception as e:
            print(f"AFT Registration failed: {e}")
        
        # Method 2: Standard unlock with correct asset number
        print("Method 2: Standard unlock with correct asset number")
        unlock_result = money.komut_unlock_machine()
        print(f"Standard unlock result: {unlock_result}")
        await asyncio.sleep(2)
        
        # Method 2.5: Machine enable (prerequisite for some machines)
        print("Method 2.5: Machine enable")
        enable_result = money.komut_machine_enable()
        print(f"Machine enable result: {enable_result}")
        await asyncio.sleep(1)
        
        # Method 2.6: Clear host controls
        print("Method 2.6: Clear host controls")
        clear_result = money.komut_clear_host_controls()
        print(f"Clear host controls result: {clear_result}")
        await asyncio.sleep(1)
        
        # Method 2.7: Advanced unlock sequence
        print("Method 2.7: Advanced unlock sequence")
        advanced_unlock_result = money.komut_advanced_unlock()
        print(f"Advanced unlock result: {advanced_unlock_result}")
        await asyncio.sleep(2)
        
        # Method 3: Check AFT status after registration and unlock
        print("Method 3: Check AFT status")
        try:
            status_result = money.check_aft_status()
            print(f"AFT Status check result: {status_result}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"AFT Status check failed: {e}")
        
        # Method 4: Check balance to see if unlock worked
        print("Method 4: Check balance after unlock")
        balance_result3 = money.komut_bakiye_sorgulama("unlock_test", False, "post_unlock_check")
        balance_received3 = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received3:
            print("✅ Post-unlock balance query successful")
            # Check lock status from communicator
            if hasattr(money.communicator, 'last_game_lock_status'):
                lock_status = money.communicator.last_game_lock_status
                aft_status = money.communicator.last_aft_status
                print(f"📊 Current Lock Status: {lock_status}")
                print(f"📊 Current AFT Status: {aft_status}")
                
                if lock_status == "FF":
                    print("❌ Machine is still fully locked")
                elif lock_status == "00":
                    print("✅ Machine is fully unlocked!")
                else:
                    print(f"⚠️  Machine partially locked: {lock_status}")
            else:
                print("⚠️  No lock status information available")
        else:
            print("⚠️  Post-unlock balance query failed")
        
        print("\n=== Final Balance Check ===")
        # Check balance after unlock attempts
        balance_result2 = money.komut_bakiye_sorgulama("unlock_test", False, "post_unlock_balance")
        balance_received2 = await money.wait_for_bakiye_sorgulama_completion(timeout=5)
        
        if balance_received2:
            print("✅ Final balance query successful")
        else:
            print("⚠️  Final balance query failed")
        
        print(f"Final balance: Cashable=${money.yanit_bakiye_tutar}, Restricted=${money.yanit_restricted_amount}, Non-restricted=${money.yanit_nonrestricted_amount}")
        
        # Method 5: Try a small test transfer if machine appears unlocked
        if money.yanit_bakiye_tutar > 0 or balance_received2:
            print("\n=== Test AFT Transfer ===")
            try:
                # Try a small $1.00 transfer
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
                if transfer_success:
                    print("✅ Test transfer successful!")
                elif transfer_success is False:
                    print("❌ Test transfer failed")
                else:
                    print("⚠️  Test transfer timed out")
                    
            except Exception as e:
                print(f"Test transfer error: {e}")
        
        # Give some time for any final responses
        print("\n=== Final Communication Check ===")
        for i in range(3):
            await asyncio.sleep(1)
            print(f"Final check {i+1}/3...")
        
    except Exception as e:
        print(f"Error in unlock test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nCleaning up...")
        tester.stop_polling()
        communicator.close_port()
        print("✅ Port closed")

if __name__ == "__main__":
    asyncio.run(test_machine_unlock()) 