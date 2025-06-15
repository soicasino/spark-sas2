#!/usr/bin/env python3
"""
Definitive AFT Transfer Test - Exact Original Logic

This script uses the EXACT command construction logic from raspberryPython_orj.py
with the blocking state-based mechanism for waiting for AFT completion.

Key differences from previous attempts:
1. Exact BCD formatting from original AddLeftBCD function
2. Correct command length calculation 
3. Proper Transfer Flags and all required fields
4. Blocking wait mechanism with global status flags
"""

import sys
import os
import time
import threading
from typing import Optional
from crccheck.crc import CrcKermit

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_communicator import SASCommunicator
from config_manager import ConfigManager

class OriginalAFTSystem:
    """
    AFT System using the EXACT logic from raspberryPython_orj.py
    """
    
    def __init__(self):
        self.config = ConfigManager()
        self.communicator = None
        self.running = False
        self.poll_thread = None
        
        # Global state flags (matching original design)
        self.IsWaitingForParaYukle = 0
        self.Global_ParaYukleme_TransferStatus = "FF"  # FF = pending
        
    def start(self):
        """Initialize SAS communication"""
        print("Initializing SAS communication...")
        
        sas_port = self.config.get('sas', 'port', '/dev/ttyUSB1')
        print(f"Connecting to SAS port: {sas_port}")
        
        self.communicator = SASCommunicator(sas_port, self.config)
        
        if not self.communicator.open_port():
            raise ConnectionError("Failed to open SAS port. Check connection and permissions.")
        
        if not self.communicator.is_port_open:
            raise ConnectionError("SAS port failed to open properly.")
        
        print("✅ SAS communication initialized.")
        
        # Start background polling (equivalent to DoSASPoolingMsg timer)
        self.running = True
        self.poll_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.poll_thread.start()
        
    def stop(self):
        """Stop polling and close port"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1)
        if self.communicator:
            self.communicator.close_port()
        print("Polling stopped and port closed.")
    
    def _polling_loop(self):
        """
        Continuous background polling - equivalent to DoSASPoolingMsg
        This runs perpetually and handles all incoming SAS messages
        """
        print("[POLLING] Background polling started...")
        while self.running:
            try:
                if self.communicator and self.communicator.is_port_open:
                    # Get any incoming data
                    data = self.communicator.get_data_from_sas_port()
                    if data:
                        print(f"[POLLING] RX: {data}")
                        # Handle the response (equivalent to HandleReceivedSASCommand)
                        self._handle_received_sas_command(data)
                        
                    # Send periodic general polls
                    self.communicator.send_general_poll()
                
                time.sleep(0.1)  # 100ms polling interval
                
            except Exception as e:
                print(f"[POLLING] Error: {e}")
                time.sleep(1)
        
        print("[POLLING] Stopped.")
    
    def _handle_received_sas_command(self, data: str):
        """
        Handle incoming SAS commands - equivalent to HandleReceivedSASCommand
        """
        if not data:
            return
            
        # Check if this is an AFT response (72h command)
        if data.startswith("0172"):
            print(f"[HANDLER] AFT Response detected: {data}")
            self._yanit_para_yukle(data)
        elif data == "69":
            print("[HANDLER] AFT Completion signal (69h) received")
            # Some machines send 69h as completion signal
            self.Global_ParaYukleme_TransferStatus = "00"
    
    def _yanit_para_yukle(self, response: str):
        """
        Handle AFT response - equivalent to Yanit_ParaYukle
        Extracts the Transfer Status and updates global flag
        """
        print(f"[YANIT_PARA_YUKLE] Processing AFT response: {response}")
        
        try:
            # Extract Transfer Status from response
            # In 72h response: Address(2) + Command(2) + Length(2) + TransferStatus(2)
            if len(response) >= 8:
                transfer_status = response[6:8]  # Status at position 6-7
                print(f"[YANIT_PARA_YUKLE] Transfer Status: {transfer_status}")
                
                # Update global status flag
                self.Global_ParaYukleme_TransferStatus = transfer_status
                
                # Status codes:
                # 00 = Success
                # 87 = Door open
                # 84 = Transfer limit exceeded
                # etc.
                
        except Exception as e:
            print(f"[YANIT_PARA_YUKLE] Error parsing response: {e}")
            self.Global_ParaYukleme_TransferStatus = "FF"  # Error
    
    def AddLeftBCD(self, numbers, length_in_bytes):
        """
        EXACT implementation of AddLeftBCD from original working code
        """
        numbers = int(numbers)
        retdata = str(numbers)
        
        # Ensure even number of digits
        if len(retdata) % 2 == 1:
            retdata = "0" + retdata
        
        # Calculate padding needed
        count_number = len(retdata) // 2
        padding_needed = length_in_bytes - count_number
        
        # Add padding
        for _ in range(padding_needed):
            retdata = "00" + retdata
            
        return retdata
    
    def GetCRC(self, command):
        """
        EXACT implementation of GetCRC from original working code
        """
        try:
            data = bytearray.fromhex(command)
            crc_instance = CrcKermit()
            crc_instance.process(data)
            crc_bytes = crc_instance.finalbytes()
            crc_hex = crc_bytes.hex().upper().zfill(4)
            
            # SAS requires CRC bytes to be reversed
            return command + crc_hex[2:4] + crc_hex[0:2]
            
        except Exception as e:
            print(f"[CRC] Error calculating CRC: {e}")
            return command + "0000"
    
    def Komut_ParaYukle(self, customerbalance=0.0, customerpromo=0.0, assetnumber="0000006C", 
                       registrationkey="0000000000000000000000000000000000000000", transactionid=None):
        """
        EXACT implementation of Komut_ParaYukle from original working code
        This builds the AFT command exactly as the original did
        """
        print(f"[KOMUT_PARA_YUKLE] Starting AFT transfer - Amount: ${customerbalance}, Promo: ${customerpromo}")
        
        # Generate transaction ID if not provided
        if transactionid is None:
            transactionid = int(time.time()) % 10000
        
        print(f"[KOMUT_PARA_YUKLE] Using Transaction ID: {transactionid}")
        
        # Convert amounts to cents
        amount_cents = int(customerbalance * 100)
        promo_cents = int(customerpromo * 100)
        
        # Build command exactly as original
        Command = ""
        Command += "00"  # Transfer Code
        Command += "00"  # Transfer Index  
        Command += "00"  # Transfer Type (00 = Cashable, matching original)
        Command += self.AddLeftBCD(amount_cents, 5)  # Cashable amount
        Command += self.AddLeftBCD(promo_cents, 5)   # Restricted amount
        Command += "0000000000"  # Non-restricted amount (5 bytes)
        Command += "07"  # Transfer Flags (Hard mode)
        Command += assetnumber  # Asset Number (4 bytes)
        Command += registrationkey  # Registration Key (20 bytes)
        
        # Transaction ID - EXACT original logic
        transaction_id_str = str(transactionid)
        transaction_id_hex = ''.join('{:02x}'.format(ord(c)) for c in transaction_id_str)
        Command += self.AddLeftBCD(len(transaction_id_hex) // 2, 1)  # Length of transaction ID
        Command += transaction_id_hex  # Transaction ID in hex
        
        Command += "00000000"  # Expiration Date (4 bytes)
        Command += "0000"      # Pool ID (2 bytes)
        Command += "00"        # Receipt Data Length
        
        # Build final command with header
        sas_address = "01"
        command_code = "72"
        
        # Calculate length - EXACT original method
        command_length_hex = hex(int(len(Command)/2)).replace("0x", "").upper().zfill(2)
        
        # Assemble final command
        final_command_no_crc = sas_address + command_code + command_length_hex + Command
        
        # Add CRC
        final_command = self.GetCRC(final_command_no_crc)
        
        print(f"[KOMUT_PARA_YUKLE] Final AFT Command: {final_command}")
        print(f"[KOMUT_PARA_YUKLE] Command breakdown:")
        print(f"  Header: {sas_address}{command_code}{command_length_hex}")
        print(f"  Body: {Command}")
        print(f"  Length: {len(Command)//2} bytes")
        
        # Send command
        result = self.communicator.sas_send_command_with_queue("ParaYukle", final_command, 1)
        print(f"[KOMUT_PARA_YUKLE] Command sent successfully: {result}")
        
        return transactionid
    
    def Wait_ParaYukle(self, timeout_seconds=30):
        """
        EXACT implementation of Wait_ParaYukle from original working code
        Blocking wait with global status flag checking
        """
        print("[WAIT_PARA_YUKLE] Starting blocking wait for AFT completion...")
        
        # Set waiting flag
        self.IsWaitingForParaYukle = 1
        
        start_time = time.time()
        
        # Blocking while loop - exactly as original
        while self.IsWaitingForParaYukle == 1:
            # Check if we got a response
            if self.Global_ParaYukleme_TransferStatus != "FF":
                print(f"[WAIT_PARA_YUKLE] Transfer completed with status: {self.Global_ParaYukleme_TransferStatus}")
                
                # Reset flags
                self.IsWaitingForParaYukle = 0
                
                # Return success/failure based on status
                if self.Global_ParaYukleme_TransferStatus == "00":
                    return True
                else:
                    return False
            
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                print("[WAIT_PARA_YUKLE] Timeout waiting for AFT response")
                self.IsWaitingForParaYukle = 0
                return False
            
            # Small delay to prevent busy waiting
            time.sleep(0.1)
        
        return False
    
    def run_full_aft_test(self):
        """
        Execute the complete AFT test using original blocking mechanism
        """
        print("\n" + "="*60)
        print("DEFINITIVE AFT TEST - ORIGINAL WORKING LOGIC")
        print("="*60)
        
        try:
            # Step 1: Send AFT transfer command
            print("\n--- STEP 1: Sending AFT Transfer Command ---")
            
            # Reset status flag
            self.Global_ParaYukleme_TransferStatus = "FF"
            
            # Send the transfer command
            transaction_id = self.Komut_ParaYukle(
                customerbalance=2.0,
                assetnumber="0000006C"
            )
            
            print(f"Transfer command sent with transaction ID: {transaction_id}")
            
            # Step 2: Wait for completion using original blocking method
            print("\n--- STEP 2: Waiting for AFT completion (blocking) ---")
            
            success = self.Wait_ParaYukle(timeout_seconds=30)
            
            if success:
                print("\n--- ✅ AFT Transfer Succeeded! ---")
                print("The transfer was completed successfully using original logic.")
                return True
            else:
                print("\n--- ❌ AFT Transfer Failed ---")
                print(f"Final status: {self.Global_ParaYukleme_TransferStatus}")
                return False
                
        except Exception as e:
            print(f"\n--- ❌ Error during AFT test: {e} ---")
            return False

def main():
    """Main function to run the definitive AFT test"""
    tester = OriginalAFTSystem()
    
    try:
        tester.start()
        time.sleep(2)  # Allow polling to stabilize
        
        success = tester.run_full_aft_test()
        
        if success:
            print("\n🎯 AFT TEST COMPLETED SUCCESSFULLY!")
            print("Now check if the coin-in meters have been updated.")
        else:
            print("\n❌ AFT TEST FAILED")
            print("Check the logs above for details.")
            
    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
    finally:
        tester.stop()

if __name__ == "__main__":
    main() 