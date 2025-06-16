#!/usr/bin/env python3
"""
Test script to check AFT capability and configuration on the slot machine.
This will help determine if AFT is properly enabled.
"""

import sys
import time
from sas_communicator import SASCommunicator

def check_aft_capability(sas_comm):
    """Check if the machine supports AFT transfers"""
    print("\n🔍 Checking AFT Capability...")
    
    try:
        # Send AFT capability query (SAS command 73h)
        print("[AFT CHECK] Sending AFT capability query...")
        
        # Command 73h queries AFT capabilities
        capability_cmd = "017300A8E5"  # Basic AFT capability query
        result = sas_comm.sas_send_command_with_queue("AFTCapability", capability_cmd, 3)
        print(f"[AFT CHECK] Capability query result: {result}")
        
        return result is not None
        
    except Exception as e:
        print(f"❌ Error checking AFT capability: {e}")
        return False

def check_machine_status(sas_comm):
    """Check detailed machine status"""
    print("\n📊 Checking Machine Status...")
    
    try:
        # Get current balance and status
        balance_result = sas_comm.sas_money.komut_balance_query("0000006c")
        print(f"[STATUS] Balance query result: {balance_result}")
        
        if hasattr(sas_comm, 'last_lock_status'):
            lock_status = sas_comm.last_lock_status
            print(f"[STATUS] Current lock status: {lock_status}")
            
            # Decode lock status
            if lock_status:
                lock_int = int(lock_status, 16) if isinstance(lock_status, str) else lock_status
                print(f"[STATUS] Lock status breakdown:")
                print(f"  Bit 0 (Machine disabled): {'LOCKED' if lock_int & 0x01 else 'UNLOCKED'}")
                print(f"  Bit 1 (Progressive lockup): {'LOCKED' if lock_int & 0x02 else 'UNLOCKED'}")
                print(f"  Bit 2 (Machine tilt): {'LOCKED' if lock_int & 0x04 else 'UNLOCKED'}")
                print(f"  Bit 3 (Cash door open): {'LOCKED' if lock_int & 0x08 else 'UNLOCKED'}")
                print(f"  Bit 4 (Logic door open): {'LOCKED' if lock_int & 0x10 else 'UNLOCKED'}")
                print(f"  Bit 5 (Bill acceptor door): {'LOCKED' if lock_int & 0x20 else 'UNLOCKED'}")
                print(f"  Bit 6 (Memory error): {'LOCKED' if lock_int & 0x40 else 'UNLOCKED'}")
                print(f"  Bit 7 (Gaming locked): {'LOCKED' if lock_int & 0x80 else 'UNLOCKED'}")
        
        if hasattr(sas_comm, 'last_aft_status'):
            aft_status = sas_comm.last_aft_status
            print(f"[STATUS] Current AFT status: {aft_status}")
            
            # Decode AFT status
            if aft_status:
                aft_int = int(aft_status, 16) if isinstance(aft_status, str) else aft_status
                print(f"[STATUS] AFT status breakdown:")
                print(f"  Bit 0 (AFT registered): {'YES' if aft_int & 0x01 else 'NO'}")
                print(f"  Bit 1 (AFT enabled): {'YES' if aft_int & 0x02 else 'NO'}")
                print(f"  Bit 2 (AFT transfer pending): {'YES' if aft_int & 0x04 else 'NO'}")
                print(f"  Bit 3 (AFT transfer in progress): {'YES' if aft_int & 0x08 else 'NO'}")
                print(f"  Bit 4 (Machine cashout mode): {'YES' if aft_int & 0x10 else 'NO'}")
                print(f"  Bit 5 (Host cashout enabled): {'YES' if aft_int & 0x20 else 'NO'}")
                print(f"  Bit 6 (AFT bonus mode): {'YES' if aft_int & 0x40 else 'NO'}")
                print(f"  Bit 7 (Machine locked): {'YES' if aft_int & 0x80 else 'NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking machine status: {e}")
        return False

def try_aft_reset(sas_comm):
    """Try to reset AFT system"""
    print("\n🔄 Attempting AFT System Reset...")
    
    try:
        # Try AFT system reset commands
        reset_commands = [
            ("AFT Cancel All", "017201800BB4"),  # Cancel any pending transfers
            ("AFT Clear Registration", "017300A8E5"),  # Clear AFT registration
            ("Machine Reset", "0102CA3A"),  # General machine reset
        ]
        
        for name, cmd in reset_commands:
            print(f"[RESET] Sending {name}: {cmd}")
            result = sas_comm.sas_send_command_with_queue(name, cmd, 2)
            print(f"[RESET] {name} result: {result}")
            time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during AFT reset: {e}")
        return False

def main():
    print("🔧 AFT Capability and Configuration Tester")
    print("This script will check if AFT is properly enabled on your machine.")
    
    try:
        # Initialize SAS communication
        sas_comm = SASCommunicator()
        if not sas_comm.initialize():
            print("❌ Failed to initialize SAS communication")
            return
        
        print("✅ SAS communication initialized")
        
        # Step 1: Check AFT capability
        aft_capable = check_aft_capability(sas_comm)
        
        # Step 2: Check machine status
        status_ok = check_machine_status(sas_comm)
        
        # Step 3: Try AFT reset
        reset_ok = try_aft_reset(sas_comm)
        
        # Step 4: Try simple registration test
        print("\n🧪 Testing Simple AFT Registration...")
        try:
            reg_result = sas_comm.sas_money.komut_aft_registration(
                "0000006c", 
                "00000000000000000000000000000000000000000000", 
                "TEST01"
            )
            print(f"[REG TEST] Registration result: {reg_result}")
        except Exception as e:
            print(f"❌ Registration test error: {e}")
        
        # Summary
        print(f"\n📋 DIAGNOSTIC SUMMARY:")
        print(f"AFT Capability: {'✅' if aft_capable else '❌'}")
        print(f"Status Check: {'✅' if status_ok else '❌'}")
        print(f"Reset Commands: {'✅' if reset_ok else '❌'}")
        
        if not aft_capable:
            print(f"\n⚠️  AFT may not be enabled on this machine.")
            print(f"Check machine configuration or contact manufacturer.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            sas_comm.close()
        except:
            pass

if __name__ == "__main__":
    main() 