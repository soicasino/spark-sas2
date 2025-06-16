# SAS Money-Related Functions Implementation
# Reference: docs/para_commands.py, docs/sas-protocol-info.md, and sample SAS code
# Implements: AFT (Advanced Funds Transfer), balance query, cashout, transfer, and related money operations

import datetime
import time
import asyncio
from decimal import Decimal
from threading import Thread
from utils import get_crc, add_left_bcd

class SasMoney:
    """
    Money-related SAS protocol logic. Expects a communicator instance for sending commands.
    """
    def __init__(self, config, communicator):
        self.config = config
        self.communicator = communicator  # Should provide send_sas_command or sas_send_command_with_queue
        self.last_para_yukle_date = datetime.datetime.now()
        self.last_para_sifirla_date = datetime.datetime.now()
        self.yanit_bakiye_tutar = 0
        self.yanit_restricted_amount = 0
        self.yanit_nonrestricted_amount = 0
        self.yanit_restricted_pool_id = "0030"
        self.sifirla_first_transaction = 0
        self.sifirla_last_transaction = 0
        self.yukle_first_transaction = 0
        self.yukle_last_transaction = 0
        self.global_para_yukleme_transfer_status = None
        self.global_para_silme_transfer_status = None
        self.global_para_sifirla_84 = 0
        self.is_waiting_for_para_yukle = 0
        self.is_waiting_for_bakiye_sifirla = 0
        self.is_waiting_for_meter = False
        self.meter_response_received = False  # New flag to prevent multiple processing
        self.last_parsed_meters = {}  # Store parsed meters for API access
        # Transaction ID management
        self.current_transaction_id = int(datetime.datetime.now().timestamp()) % 10000
        # Balance query wait logic
        self.is_waiting_for_bakiye_sorgulama = False
        self.balance_query_timeout = 5  # seconds
        # ... add other state as needed

    def get_next_transaction_id(self):
        """Get the next transaction ID, incrementing the internal counter"""
        self.current_transaction_id = (self.current_transaction_id + 1) % 10000
        return self.current_transaction_id

    async def wait_for_para_yukle_completion(self, timeout=10):
        """
        Wait for the ParaYukle (money load) transfer to complete.
        Returns True if successful, False if failed, or None if timeout.
        
        This matches the original Wait_ParaYukle blocking pattern:
        1. Reset status to "PENDING" 
        2. Enter monitoring loop checking global status
        3. Exit when status changes from "PENDING"
        """
        start = time.time()
        
        print(f"[AFT WAIT] Starting AFT money load wait (timeout={timeout}s)")
        
        # CRITICAL: Reset status before waiting, matching original Wait_ParaYukle logic
        # In original: Global_ParaYukleme_TransferStatus = "PENDING" 
        self.global_para_yukleme_transfer_status = "PENDING"
        print(f"[AFT WAIT] Reset status to PENDING, starting wait loop...")
        
        while time.time() - start < timeout:
            # Add a small delay before checking status to allow background thread to update
            await asyncio.sleep(0.1)
            
            status = self.global_para_yukleme_transfer_status
            elapsed = time.time() - start
            
            # Only log every 2 seconds to avoid spam
            if elapsed > 1 and int(elapsed) % 2 == 0:
                print(f"[AFT WAIT] {elapsed:.1f}s - Current status: {status}")
            
            # Check if status has changed from "PENDING" - this means we got a response
            if status != "PENDING":
                if status == "00":  # Success
                    self.is_waiting_for_para_yukle = 0
                    print(f"[AFT WAIT] SUCCESS after {elapsed:.2f}s")
                    return True
                elif status in ("84", "87", "81", "FF"):  # Error codes
                    self.is_waiting_for_para_yukle = 0
                    print(f"[AFT WAIT] FAILED after {elapsed:.2f}s with status: {status}")
                    return False
                elif status in ("40", "C0", "C1", "C2"):  # Pending/in-progress codes - keep waiting
                    print(f"[AFT WAIT] Transfer {self.get_transfer_status_description(status).lower()}, continuing to wait...")
                    pass
                else:
                    print(f"[AFT WAIT] Unknown status: {status} - {self.get_transfer_status_description(status)}")
                
            # Check every 500ms instead of immediately looping
            await asyncio.sleep(0.4)  # Total 0.5s with the 0.1s above
            
        # Timeout
        self.is_waiting_for_para_yukle = 0
        print(f"[AFT WAIT] TIMEOUT after {timeout}s - no response from machine")
        print(f"[AFT WAIT] Final status: {self.global_para_yukleme_transfer_status}")
        return None

    def wait_for_para_yukle_completion_blocking(self, timeout=15):
        """
        Wait for AFT transfer completion - SIMPLIFIED to match working code exactly
        
        This exactly matches the original Wait_ParaYukle blocking pattern:
        1. Reset status to "PENDING" 
        2. Set waiting flag to 1
        3. Loop until status changes from "PENDING"
        4. Wait loop clears the flag (not the response handler)
        """
        start_time = time.time()
        
        print(f"[AFT WAIT] Starting AFT wait (timeout={timeout}s)")
        
        # CRITICAL: Reset status before waiting - matches original exactly
        self.global_para_yukleme_transfer_status = "PENDING"
        self.is_waiting_for_para_yukle = 1
        
        print(f"[AFT WAIT] Status reset to: PENDING")
        print(f"[AFT WAIT] Waiting flag set to: 1")
        
        # Main wait loop - EXACTLY like working code
        while self.is_waiting_for_para_yukle == 1:
            time.sleep(0.003)  # Match original timing (3ms)
            
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"[AFT WAIT] ❌ TIMEOUT after {timeout} seconds")
                self.is_waiting_for_para_yukle = 0  # Clear flag on timeout
                return None
            
            # Get current status
            status = self.global_para_yukleme_transfer_status
            
            # Check if status changed from PENDING
            if status != "PENDING":
                print(f"[AFT WAIT] Status changed from PENDING to: {status}")
                
                # CRITICAL: Clear flag here in wait loop, not in response handler
                # This matches the original working code pattern exactly
                self.is_waiting_for_para_yukle = 0
                
                print(f"[AFT WAIT] Waiting flag cleared by wait loop: {self.is_waiting_for_para_yukle}")
                
                # Return result based on status
                if status == "00":
                    print(f"[AFT WAIT] ✅ TRANSFER SUCCESSFUL")
                    return True
                else:
                    status_desc = self.get_transfer_status_description(status)
                    print(f"[AFT WAIT] ❌ TRANSFER FAILED: {status} - {status_desc}")
                    return False
        
        # Should not reach here, but handle gracefully
        print(f"[AFT WAIT] ⚠️  Wait loop exited unexpectedly")
        return None

    async def wait_for_para_sifirla_completion(self, timeout=10):
        """
        Wait for the ParaSifirla (cashout) transfer to complete.
        Returns True if successful, False if failed, or None if timeout.
        """
        start = time.time()
        self.is_waiting_for_bakiye_sifirla = 1
        
        while time.time() - start < timeout:
            status = self.global_para_silme_transfer_status
            
            if status == "00":  # Success
                self.is_waiting_for_bakiye_sifirla = 0
                return True
            elif status in ("84", "87", "81"):  # Error codes
                self.is_waiting_for_bakiye_sifirla = 0
                return False
            elif status == "40":  # Transfer pending - keep waiting
                pass
                
            await asyncio.sleep(0.2)
            
        # Timeout
        self.is_waiting_for_bakiye_sifirla = 0
        return None

    def get_transfer_status_description(self, status_code):
        """Get human-readable description of transfer status codes"""
        status_descriptions = {
            "00": "Transfer successful",
            "40": "Transfer pending",
            "80": "Machine not registered for AFT",
            "81": "Transaction ID not unique",
            "82": "Registration key mismatch", 
            "83": "No POS ID configured",
            "84": "Transfer amount exceeds machine limit",
            "87": "Gaming machine unable to accept transfers (door open, tilt, etc.)",
            "C0": "Transfer request acknowledged/pending",
            "C1": "Transfer in progress",
            "C2": "Transfer partially complete",
            "FF": "Transfer failed - general error"
        }
        return status_descriptions.get(status_code, f"Unknown status: {status_code}")

    def komut_cancel_aft_transfer(self):
        """
        Cancel any pending AFT transfer operation using the CORRECT SAS protocol command.
        This is the proper way to unlock a machine that is stuck in AFT Game Lock state.
        
        Uses the original working command: 017201800BB4
        - 01 = SAS Address
        - 72 = AFT Transfer command  
        - 01 = Length (1 byte)
        - 80 = Transfer code (Cancel/Abort transfer)
        - 0BB4 = CRC
        """
        print(f"[CANCEL AFT TRANSFER] Canceling pending AFT transfer operation")
        
        # Use the ORIGINAL working command from the reference code
        # This is the CORRECT SAS protocol format for AFT cancel
        command = "017201800BB4"
        
        print(f"[CANCEL AFT TRANSFER] Sending standard AFT cancel command: {command}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("CancelAFT", command, 1)
            print(f"[CANCEL AFT TRANSFER] Cancel AFT result: {result}")
            
            # Wait a moment for the machine to process the cancellation
            import time
            time.sleep(1)
            
            # Query status to verify the AFT lock was released
            print(f"[CANCEL AFT TRANSFER] Verifying AFT lock release...")
            self.komut_bakiye_sorgulama("aft_cancel_verify", False, "aft_cancel_verification")
            
            time.sleep(1)
            
            # Check if the AFT lock was successfully released
            if hasattr(self.communicator, 'last_game_lock_status'):
                lock_status = self.communicator.last_game_lock_status
                aft_status = getattr(self.communicator, 'last_aft_status', 'FF')
                
                print(f"[CANCEL AFT TRANSFER] Post-cancel Lock Status: {lock_status}")
                print(f"[CANCEL AFT TRANSFER] Post-cancel AFT Status: {aft_status}")
                
                if lock_status == "00":
                    print(f"[CANCEL AFT TRANSFER] ✅ SUCCESS: AFT lock successfully released!")
                    return True
                elif lock_status != "FF":
                    print(f"[CANCEL AFT TRANSFER] ⚠️  PARTIAL SUCCESS: Lock status improved to {lock_status}")
                    return True
                else:
                    print(f"[CANCEL AFT TRANSFER] ❌ AFT lock still active - may need additional steps")
                    return False
            else:
                print(f"[CANCEL AFT TRANSFER] ⚠️  Cannot verify - no status available")
                return None
                
        except Exception as e:
            print(f"[CANCEL AFT TRANSFER] Error canceling AFT transfer: {e}")
            return False

    def komut_cancel_balance_lock(self):
        """
        Cancel balance lock using the original working command.
        This is another method from the original code to clear AFT locks.
        """
        print(f"[CANCEL BALANCE LOCK] Canceling balance lock")
        
        # Original command from raspberryPython_orj.py: GetCRC("017480030000")
        # We need to calculate the CRC for this command
        command_without_crc = "017480030000"
        command = get_crc(command_without_crc)
        
        print(f"[CANCEL BALANCE LOCK] Sending balance lock cancel: {command}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("CancelBalanceLock", command, 1)
            print(f"[CANCEL BALANCE LOCK] Cancel balance lock result: {result}")
            return result
        except Exception as e:
            print(f"[CANCEL BALANCE LOCK] Error canceling balance lock: {e}")
            return False

    def komut_comprehensive_aft_unlock(self):
        """
        Comprehensive AFT unlock - sends specific commands to cancel pending AFT state
        This resolves the lock_status: FF, aft_status: B0 issue
        """
        try:
            print("[AFT UNLOCK] Starting comprehensive AFT unlock sequence...")
            
            # Step 1: Send AFT cancel command
            print("[AFT UNLOCK] Sending AFT cancel command...")
            result1 = self.komut_cancel_aft_transfer()
            print(f"[AFT UNLOCK] AFT cancel result: {result1}")
            
            # Wait for response
            time.sleep(1)
            
            # Step 2: Send general machine unlock if needed
            print("[AFT UNLOCK] Sending general machine unlock...")
            try:
                unlock_result = self.komut_unlock_machine()
                print(f"[AFT UNLOCK] General unlock result: {unlock_result}")
            except Exception as e:
                print(f"[AFT UNLOCK] General unlock error (may be normal): {e}")
            
            # Step 3: Clear any pending AFT states
            print("[AFT UNLOCK] Clearing AFT states...")
            time.sleep(1)
            
            print("[AFT UNLOCK] Comprehensive unlock sequence completed")
            return True
            
        except Exception as e:
            print(f"[AFT UNLOCK] Error in comprehensive unlock: {e}")
            return False

    def komut_aft_registration(self, asset_number, registration_key, pos_id):
        """
        AFT Registration command (73h) - required before AFT transfers
        """
        try:
            print("[AFT REGISTRATION] Starting AFT registration process")
            print(f"[AFT REGISTRATION]   Asset Number: {asset_number}")
            print(f"[AFT REGISTRATION]   Registration Key: {registration_key}")
            print(f"[AFT REGISTRATION]   POS ID: {pos_id}")
            
            # Step 1: Initialize registration
            print("[AFT REGISTRATION] Step 1: Initialize registration")
            init_command = "017301FFA765"  # AFT registration init
            result1 = self.communicator.sas_send_command_with_queue("AFTRegInit", init_command, 1)
            print(f"[AFT REGISTRATION] Init command result: {result1}")
            
            time.sleep(1)
            
            # Step 2: Complete registration with asset number and POS ID
            print("[AFT REGISTRATION] Step 2: Complete registration")
            
            # Convert POS ID to BCD format (4 bytes)
            pos_id_padded = pos_id.ljust(4, '\x00')[:4]  # Pad to 4 characters
            pos_id_bcd = ''.join('{:02x}'.format(ord(c)) for c in pos_id_padded)
            print(f"[AFT REGISTRATION] POS ID BCD: {pos_id_bcd}")
            
            # CRITICAL FIX: Asset number should be used as-is in hex format, NOT converted to BCD!
            # The machine expects the asset number in little-endian hex format, not BCD
            asset_bcd = asset_number.upper().zfill(8)  # Just ensure 8 characters, don't convert to BCD
            print(f"[AFT REGISTRATION] Asset Number (hex): {asset_bcd}")
            
            # Registration key is already in correct format (20 bytes hex = 40 chars)
            print(f"[AFT REGISTRATION] Registration Key: {registration_key}")
            
            # Build complete registration command
            sas_address = "01"
            command_code = "73"
            # CRITICAL FIX: Registration code should be "00" for normal registration, not "01"
            # Format: RegCode + AssetNumber + RegKey + POSID (all BCD encoded)
            registration_code = "00"  # 00 = Normal registration (not 01)
            command_body = registration_code + asset_bcd + registration_key + pos_id_bcd
            command_length = hex(len(command_body) // 2).replace("0x", "").upper().zfill(2)
            
            complete_command_no_crc = sas_address + command_code + command_length + command_body
            complete_command = self._get_crc_original(complete_command_no_crc)
            
            print(f"[AFT REGISTRATION] Command structure breakdown:")
            print(f"[AFT REGISTRATION]   SAS Address: {sas_address}")
            print(f"[AFT REGISTRATION]   Command Code: {command_code}")
            print(f"[AFT REGISTRATION]   Length: {command_length}")
            print(f"[AFT REGISTRATION]   Registration Code: {registration_code}")
            print(f"[AFT REGISTRATION]   Asset Number BCD: {asset_bcd}")
            print(f"[AFT REGISTRATION]   Registration Key: {registration_key}")
            print(f"[AFT REGISTRATION]   POS ID BCD: {pos_id_bcd}")
            print(f"[AFT REGISTRATION] Complete registration command: {complete_command}")
            result2 = self.communicator.sas_send_command_with_queue("AFTRegComplete", complete_command, 1)
            print(f"[AFT REGISTRATION] Complete registration result: {result2}")
            
            print("[AFT REGISTRATION] AFT registration completed")
            return True
            
        except Exception as e:
            print(f"[AFT REGISTRATION] Error in AFT registration: {e}")
            return False

    def komut_read_asset_number(self):
        """
        Read the asset number from the gaming machine using SAS command 73h.
        This should be called at startup to get the machine's actual asset number.
        
        Returns:
            Result of the asset number query command
        """
        print(f"[ASSET NUMBER] Reading asset number from machine")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Send AFT registration status query (code FF)
        command = f"{sas_address}7301FF"
        command_crc = get_crc(command)
        
        print(f"[ASSET NUMBER] Sending asset number query: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("ReadAssetNo", command_crc, 1)
            print(f"[ASSET NUMBER] Asset number query result: {result}")
            return result
        except Exception as e:
            print(f"[ASSET NUMBER] Error reading asset number: {e}")
            raise

    async def wait_for_bakiye_sorgulama_completion(self, timeout=5):
        """
        Wait for the balance query to complete and balance fields to be set.
        Returns True if successful, False if failed, or None if timeout.
        """
        start = time.time()
        self.is_waiting_for_bakiye_sorgulama = True
        
        print(f"[BALANCE WAIT] Starting balance query wait (timeout={timeout}s)")
        
        while time.time() - start < timeout:
            # Add a small delay to allow background thread to process responses
            await asyncio.sleep(0.1)
            
            # Check if waiting flag has been cleared by the response handler
            if not self.is_waiting_for_bakiye_sorgulama:
                print(f"[BALANCE WAIT] Balance received successfully after {time.time() - start:.2f}s")
                print(f"[BALANCE WAIT] Cashable: {self.yanit_bakiye_tutar}, Restricted: {self.yanit_restricted_amount}, Non-restricted: {self.yanit_nonrestricted_amount}")
                return True
            
            # Also check if balance has been received (any non-zero value indicates response)
            if (self.yanit_bakiye_tutar > 0 or 
                self.yanit_restricted_amount > 0 or 
                self.yanit_nonrestricted_amount > 0):
                self.is_waiting_for_bakiye_sorgulama = False
                print(f"[BALANCE WAIT] Balance received successfully after {time.time() - start:.2f}s")
                print(f"[BALANCE WAIT] Cashable: {self.yanit_bakiye_tutar}, Restricted: {self.yanit_restricted_amount}, Non-restricted: {self.yanit_nonrestricted_amount}")
                return True
                
            # Wait before checking again
            await asyncio.sleep(0.4)  # Total 0.5s with the 0.1s above
            
        # Timeout
        self.is_waiting_for_bakiye_sorgulama = False
        print(f"[BALANCE WAIT] Timeout after {timeout}s - no balance response received")
        return False

    def komut_bakiye_sorgulama(self, sender, isforinfo, sendertext='UndefinedBakiyeSorgulama'):
        """
        Send balance query command to the machine.
        This sends SAS command 74h to query current balance.
        CORRECTED: Based on original working raspberryPython code format
        """
        print(f"[BALANCE QUERY] Starting balance query - sender: {sender}, isforinfo: {isforinfo}, text: {sendertext}")
        
        # Reset balance values before query
        self.yanit_bakiye_tutar = 0
        self.yanit_restricted_amount = 0
        self.yanit_nonrestricted_amount = 0
        
        # Set waiting flag
        self.is_waiting_for_bakiye_sorgulama = True
        
        # CRITICAL FIX: SAS 74h command format from original working code
        # The command does NOT include asset number - asset number comes back in the response!
        
        # Build command using original working logic from raspberryPython
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Original logic for different scenarios:
        is_lock_needed = False
        if isforinfo == 0:  # If balance is needed (not just for info)
            is_lock_needed = True
        
        if sender == 1:  # Money loading operations
            is_lock_needed = False
        
        # Base command format from original working code
        command = f"{sas_address}7400000000"  # Unlocked query (default)
        
        if is_lock_needed:
            # For operations that need locking
            if sender == 1:  # Money loading
                command = f"{sas_address}7400013000"  # Transfer to machine
            elif sender == 2:  # Money withdrawal  
                command = f"{sas_address}7400029000"  # Transfer from machine
            else:
                command = f"{sas_address}7400019999"  # Default transfer to machine
        
        # Device type specific adjustments (from original code)
        device_type_id = getattr(self.communicator, 'device_type_id', 0)
        if not is_lock_needed and (device_type_id == 5 or device_type_id == 9):
            command = f"{sas_address}74FF000000"  # Special unlocked format
        
        print(f"[BALANCE QUERY] Command format: {command} (sender: {sender}, lock_needed: {is_lock_needed}, device_type: {device_type_id})")
        
        # Add CRC
        command = get_crc(command)
        
        print(f"[BALANCE QUERY] Sending command: {command}")
        
        try:
            # Send the command
            result = self.communicator.sas_send_command_with_queue("MoneyQuery", command, 1)
            print(f"[BALANCE QUERY] Command sent successfully, result: {result}")
            return result
        except Exception as e:
            print(f"[BALANCE QUERY] Error sending command: {e}")
            self.is_waiting_for_bakiye_sorgulama = False
            raise

    def komut_para_yukle(self, customerbalance=0.0, customerpromo=0.0, transfertype=10, 
                         assetnumber=None, registrationkey=None, transactionid=None, auto_lock=False):
        """
        FINAL CORRECTED AFT Transfer Command - Using the exact original working command structure.
        This version includes the proper BCD and Hex formatting for all fields.
        """
        print(f"[AFT COMMAND] Building FINAL CORRECTED AFT Transfer Command")
        
        try:
            # Step 1: Get basic parameters
            sas_address = getattr(self.communicator, 'sas_address', '01')
            command_code = "72"
            
            # Step 2: Use provided asset number or get from communicator/default
            if assetnumber is None:
                assetnumber = getattr(self.communicator, 'asset_number', '0000006C')

            # Step 3: Use provided registration key or default
            if registrationkey is None:
                registrationkey = "0000000000000000000000000000000000000000"

            # Step 4: Generate transaction ID if not provided
            if transactionid is None:
                from datetime import datetime
                transactionid = str(int(datetime.now().timestamp()) % 10000)

            # Step 5: Convert amount to cents for BCD conversion
            customerbalance_cents = int(customerbalance * 100)
            customerpromo_cents = int(customerpromo * 100)

            # Step 6: Build command body with correct formatting
            CommandBody = ""
            CommandBody += "00"  # Transfer Code
            CommandBody += "00"  # Transfer Index
            
            # *** FINAL FIX #1: Use HEX formatting for transfer type ***
            CommandBody += f"{transfertype:02X}" # e.g., 10 becomes "0A"
            
            CommandBody += self._add_left_bcd_original(customerbalance_cents, 5)
            CommandBody += self._add_left_bcd_original(customerpromo_cents, 5)
            CommandBody += "0000000000"  # Non-restricted amount (5 bytes)
            
            CommandBody += "07"  # Transfer Flags (07 for hard cashout mode)
            CommandBody += assetnumber.zfill(8) # Asset number (4 bytes)
            CommandBody += registrationkey.zfill(40) # Registration key (20 bytes)

            # *** FINAL FIX #2: Use HEX formatting for transaction ID length ***
            transaction_id_hex = ''.join(f"{ord(c):02x}" for c in transactionid)
            CommandBody += f"{len(transactionid):02X}" # e.g., length 10 becomes "0A"
            CommandBody += transaction_id_hex
            
            CommandBody += "00000000"  # Expiration Date
            CommandBody += "0000"      # Pool ID
            CommandBody += "00"        # Receipt Data Length

            # Step 7: Build full command with header and CRC
            command_length_hex = f"{len(CommandBody) // 2:02X}"
            command_header = sas_address + command_code + command_length_hex
            full_command_no_crc = command_header + CommandBody
            final_command = self._get_crc_original(full_command_no_crc) # Use the correct CRC function

            print(f"[AFT COMMAND] FINAL CORRECTED COMMAND: {final_command}")

            # Step 8: Send the command
            self.communicator.sas_send_command_with_queue("ParaYukle", final_command, 1)
            
            return transactionid

        except Exception as e:
            print(f"[AFT COMMAND] ❌ Exception in komut_para_yukle: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _add_left_bcd_original(self, numbers, length_in_bytes):
        """
        EXACT implementation of AddLeftBCD from the original working code
        to correctly format numbers into a BCD hex string.
        
        This is CRITICAL for AFT transfers - the machine expects BCD format,
        not standard decimal strings.
        
        Args:
            numbers: Number to convert to BCD
            length_in_bytes: Target length in bytes (will be doubled for hex chars)
            
        Returns:
            BCD hex string of exact required length
        """
        numbers = int(numbers)
        retdata = str(numbers)

        # Ensure even number of digits for BCD pairing
        if len(retdata) % 2 == 1:
            retdata = "0" + retdata

        # Calculate how many padding bytes are needed
        current_bytes = len(retdata) // 2
        padding_bytes_needed = length_in_bytes - current_bytes

        # Add left padding with "00" bytes
        for _ in range(padding_bytes_needed):
            retdata = "00" + retdata
            
        # Ensure final string is exactly the required length in characters (bytes * 2)
        return retdata.zfill(length_in_bytes * 2)

    def _get_crc_original(self, command):
        """
        FINAL CORRECTED CRC implementation - Matches exactly the working utils.get_crc function.
        """
        try:
            from crccheck.crc import CrcKermit
            
            data = bytearray.fromhex(command)
            crc_instance = CrcKermit()
            crc_instance.process(data)
            crc_hex = crc_instance.finalbytes().hex().upper()
            crc_hex = crc_hex.zfill(4)
            
            # SAS requires the 2 CRC bytes to be reversed.
            # For a CRC of 0x0D37, the bytes are 0D and 37. They must be sent as 37 0D.
            return command + crc_hex[2:4] + crc_hex[0:2]
            
        except Exception as e:
            print(f"[CRC] Error calculating CRC: {e}")
            return command + "0000"

    def komut_para_sifirla(self, doincreaseid, transactionid, assetnumber, registrationkey):
        self.last_para_sifirla_date = datetime.datetime.now()
        
        # Use provided transaction ID or generate new one
        if doincreaseid:
            actual_transaction_id = self.get_next_transaction_id()
        else:
            actual_transaction_id = transactionid
            
        # Reset status before sending
        self.global_para_silme_transfer_status = None
        
        # FIXED: Command should start with SAS address, not asset number
        sas_address = getattr(self.communicator, 'sas_address', '01')
        command_header = sas_address + "72"
        command = "00"  # transfer code
        command += "00"  # transfer index
        command += "80"  # transfer type
        command += add_left_bcd(str(int(self.yanit_bakiye_tutar * 100)), 5)
        command += add_left_bcd(str(int(self.yanit_restricted_amount * 100)), 5)
        command += add_left_bcd(str(int(self.yanit_nonrestricted_amount * 100)), 5)
        command += "0F"  # transfer flag (hard mode)
        command += assetnumber
        command += registrationkey
        transaction_id_hex = ''.join(f"{ord(c):02x}" for c in str(actual_transaction_id))
        command += add_left_bcd(str(len(transaction_id_hex) // 2), 1)
        command += transaction_id_hex
        command += "00000000"  # expiration date
        command += self.yanit_restricted_pool_id if len(self.yanit_restricted_pool_id) == 4 else "0030"
        command += "00"  # receipt data length
        command_header += hex(len(command) // 2).replace("0x", "")
        full_command = get_crc(command_header + command)
        self.communicator.sas_send_command_with_queue("Cashout", full_command, 1)
        
        return actual_transaction_id

    def handle_aft_response(self, response_data):
        """
        Handle AFT response from the machine and update status variables.
        This should be called by your SAS polling/response handling logic.
        """
        try:
            # Parse the response to extract status code
            # This is a simplified parser - adjust based on your actual response format
            if len(response_data) >= 6:
                command = response_data[2:4]
                if command == "72":  # AFT response
                    # Extract status from response (adjust indices based on actual format)
                    status_code = response_data[6:8] if len(response_data) > 8 else "00"
                    
                    # Update appropriate status variable based on transfer type
                    if self.is_waiting_for_para_yukle:
                        self.global_para_yukleme_transfer_status = status_code
                        print(f"AFT Load Status Updated: {status_code} - {self.get_transfer_status_description(status_code)}")
                    elif self.is_waiting_for_bakiye_sifirla:
                        self.global_para_silme_transfer_status = status_code
                        print(f"AFT Cashout Status Updated: {status_code} - {self.get_transfer_status_description(status_code)}")
                        
        except Exception as e:
            print(f"Error parsing AFT response: {e}")

    def yanit_bakiye_sorgulama(self, yanit):
        """
        Handle balance query response from the machine.
        This method parses the SAS 74h response and updates balance fields.
        """
        try:
            print(f"[BALANCE RESPONSE] ===== RAW AFT BALANCE RESPONSE =====")
            print(f"[BALANCE RESPONSE] Raw response: {yanit}")
            print(f"[BALANCE RESPONSE] Response length: {len(yanit)} characters")
            print(f"[BALANCE RESPONSE] Response bytes: {' '.join([yanit[i:i+2] for i in range(0, len(yanit), 2)])}")
            print(f"[BALANCE RESPONSE] ============================================")
            
            # FIXED: Always process balance responses, don't check waiting flag
            # The waiting flag check was causing timing issues where responses
            # arrived before the async wait function could properly set up
            
            # Minimum response should be at least 20 characters (address + command + length + some data)
            if len(yanit) < 20:
                print(f"[BALANCE RESPONSE] Response too short: {len(yanit)} characters")
                return
            
            # Parse response according to SAS protocol
            # Format: Address(2) + Command(2) + Length(2) + AssetNumber(8) + GameLockStatus(2) + ...
            index = 0
            address = yanit[index:index+2]
            index += 2
            print(f"[BALANCE RESPONSE] Address: {address}")
            
            command = yanit[index:index+2]
            index += 2
            print(f"[BALANCE RESPONSE] Command: {command}")
            
            length_hex = yanit[index:index+2]
            index += 2
            print(f"[BALANCE RESPONSE] Length: {length_hex}")
            
            # Validate command is 74 (balance query response)
            if command.upper() != "74":
                print(f"[BALANCE RESPONSE] Unexpected command: {command}, expected 74")
                return
            
            # Parse length
            try:
                length = int(length_hex, 16)
                print(f"[BALANCE RESPONSE] Parsed length: {length} bytes")
            except ValueError:
                print(f"[BALANCE RESPONSE] Invalid length: {length_hex}")
                return
            
            # Check if we have enough data based on length
            expected_total_length = 6 + (length * 2)  # 6 for header + length*2 for data
            if len(yanit) < expected_total_length:
                print(f"[BALANCE RESPONSE] Incomplete response: got {len(yanit)}, expected {expected_total_length}")
                # Try to parse what we have
            
            asset_number = yanit[index:index+8] if index + 8 <= len(yanit) else "00000000"
            index += 8
            print(f"[BALANCE RESPONSE] Asset Number: {asset_number}")
            
            game_lock_status = yanit[index:index+2] if index + 2 <= len(yanit) else "00"
            index += 2
            print(f"[BALANCE RESPONSE] Game Lock Status: {game_lock_status}")
            
            available_transfers = yanit[index:index+2] if index + 2 <= len(yanit) else "00"
            index += 2
            print(f"[BALANCE RESPONSE] Available Transfers: {available_transfers}")
            
            host_cashout_status = yanit[index:index+2] if index + 2 <= len(yanit) else "00"
            index += 2
            print(f"[BALANCE RESPONSE] Host Cashout Status: {host_cashout_status}")
            
            aft_status = yanit[index:index+2] if index + 2 <= len(yanit) else "00"
            index += 2
            print(f"[BALANCE RESPONSE] AFT Status: {aft_status}")
            
            max_buffer_index = yanit[index:index+2] if index + 2 <= len(yanit) else "00"
            index += 2
            print(f"[BALANCE RESPONSE] Max Buffer Index: {max_buffer_index}")
            
            # Current cashable amount (5 bytes BCD = 10 hex characters)
            current_cashable_amount = yanit[index:index+10] if index + 10 <= len(yanit) else "0000000000"
            index += 10
            print(f"[BALANCE RESPONSE] Current Cashable Amount (raw): {current_cashable_amount}")
            print(f"[BALANCE RESPONSE] Cashable amount position in response: characters {index-10} to {index}")
            
            if len(current_cashable_amount) != 10:
                print(f"[BALANCE RESPONSE] Incomplete cashable amount: {current_cashable_amount}")
                # Use what we have, pad with zeros
                current_cashable_amount = current_cashable_amount.ljust(10, '0')
            
            # Validate BCD format
            if not self.is_valid_bcd(current_cashable_amount):
                print(f"[BALANCE RESPONSE] Invalid BCD in cashable amount: {current_cashable_amount}")
                current_cashable_amount = "0000000000"
            
            # Convert BCD to decimal (divide by 100 for cents to dollars)
            try:
                cashable_amount_raw = self.bcd_to_int(current_cashable_amount)
                cashable_amount = cashable_amount_raw / 100
                print(f"[BALANCE RESPONSE] BCD conversion: '{current_cashable_amount}' -> {cashable_amount_raw} cents -> ${cashable_amount}")
            except ValueError as e:
                print(f"[BALANCE RESPONSE] Error converting cashable amount: {current_cashable_amount}, error: {e}")
                cashable_amount = 0
            
            # Current restricted amount (5 bytes BCD)
            current_restricted_amount = yanit[index:index+10] if index + 10 <= len(yanit) else "0000000000"
            index += 10
            print(f"[BALANCE RESPONSE] Current Restricted Amount (raw): {current_restricted_amount}")
            print(f"[BALANCE RESPONSE] Restricted amount position: characters {index-10} to {index}")
            
            if not self.is_valid_bcd(current_restricted_amount):
                current_restricted_amount = "0000000000"
            
            try:
                restricted_amount_raw = self.bcd_to_int(current_restricted_amount)
                restricted_amount = restricted_amount_raw / 100
                print(f"[BALANCE RESPONSE] Restricted BCD conversion: '{current_restricted_amount}' -> {restricted_amount_raw} cents -> ${restricted_amount}")
            except ValueError as e:
                print(f"[BALANCE RESPONSE] Error converting restricted amount: {current_restricted_amount}, error: {e}")
                restricted_amount = 0
            
            # Current non-restricted amount (5 bytes BCD)
            current_nonrestricted_amount = yanit[index:index+10] if index + 10 <= len(yanit) else "0000000000"
            index += 10
            print(f"[BALANCE RESPONSE] Current Non-restricted Amount (raw): {current_nonrestricted_amount}")
            print(f"[BALANCE RESPONSE] Non-restricted amount position: characters {index-10} to {index}")
            
            if not self.is_valid_bcd(current_nonrestricted_amount):
                current_nonrestricted_amount = "0000000000"
            
            try:
                nonrestricted_amount_raw = self.bcd_to_int(current_nonrestricted_amount)
                nonrestricted_amount = nonrestricted_amount_raw / 100
                print(f"[BALANCE RESPONSE] Non-restricted BCD conversion: '{current_nonrestricted_amount}' -> {nonrestricted_amount_raw} cents -> ${nonrestricted_amount}")
            except ValueError as e:
                print(f"[BALANCE RESPONSE] Error converting non-restricted amount: {current_nonrestricted_amount}, error: {e}")
                nonrestricted_amount = 0
            
            # Update balance fields
            self.yanit_bakiye_tutar = cashable_amount
            self.yanit_restricted_amount = restricted_amount
            self.yanit_nonrestricted_amount = nonrestricted_amount
            
            # Store lock status information in communicator for UI display
            if hasattr(self.communicator, 'last_game_lock_status'):
                self.communicator.last_game_lock_status = game_lock_status
                self.communicator.last_aft_status = aft_status
                self.communicator.last_available_transfers = available_transfers
                print(f"[BALANCE RESPONSE] Lock status stored in communicator")
            else:
                # Add attributes if they don't exist
                self.communicator.last_game_lock_status = game_lock_status
                self.communicator.last_aft_status = aft_status
                self.communicator.last_available_transfers = available_transfers
                print(f"[BALANCE RESPONSE] Lock status attributes created and stored")
            
            # Clear waiting flag - this will signal the async wait function
            self.is_waiting_for_bakiye_sorgulama = False
            
            print(f"[BALANCE RESPONSE] Balance parsed successfully:")
            print(f"[BALANCE RESPONSE]   Cashable: {cashable_amount}")
            print(f"[BALANCE RESPONSE]   Restricted: {restricted_amount}")
            print(f"[BALANCE RESPONSE]   Non-restricted: {nonrestricted_amount}")
            print(f"[BALANCE RESPONSE]   Game Lock Status: {game_lock_status}")
            print(f"[BALANCE RESPONSE]   AFT Status: {aft_status}")
            print(f"[BALANCE RESPONSE]   Available Transfers: {available_transfers}")
            print(f"[BALANCE RESPONSE] Waiting flag cleared - async wait should now complete")
            
        except Exception as e:
            print(f"[BALANCE RESPONSE] Error parsing balance response: {e}")
            print(f"[BALANCE RESPONSE] Raw response: {yanit}")
            # Clear waiting flag on error to prevent infinite wait
            self.is_waiting_for_bakiye_sorgulama = False

    def komut_get_meter(self, isall=0, gameid=0):
        print("=== METER: komut_get_meter called ===")
        print(f"METER: komut_get_meter params: isall={isall}, gameid={gameid}")
        # Removed buffer clear to avoid missing fast meter responses
        G_CasinoId = int(self.config.get('casino', 'casinoid') or 8)
        IsNewMeter = 1 if G_CasinoId in [8, 11, 7] else 0
        if isall == 0 and IsNewMeter == 0:
            command = get_crc("012F0C0000A0B802031E00010BA2BA")
        elif isall == 0 and IsNewMeter == 1:
            command = get_crc("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600")
        elif isall == 1:
            command = get_crc("012F0C00000405060C191D7FFAFBFC")
        elif isall == 2:
            command = get_crc("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600")
        else:
            print(f"METER: komut_get_meter unknown isall value: {isall}")
            return
        print(f"METER: komut_get_meter sending command: {command}")
        self.communicator.sas_send_command_with_queue("getmeter2", command, 0)
        print("=== METER: komut_get_meter end ===")

    def bcd_to_int(self, bcd_str):
        """Convert a BCD string (e.g., '00012345') to an integer."""
        # Each pair of hex digits is a BCD byte
        # Convert to decimal by treating each nibble as a digit
        digits = ''
        for i in range(0, len(bcd_str), 2):
            byte = bcd_str[i:i+2]
            if len(byte) < 2:
                continue
            high = int(byte[0], 16)
            low = int(byte[1], 16)
            digits += f"{high}{low}"
        return int(digits.lstrip('0') or '0')

    METER_CODE_MAP = {
        '00': ('total_turnover', 5),
        '01': ('total_win', 5),
        '02': ('total_jackpot', 5),
        '03': ('total_handpay', 5),
        '04': ('total_cancelled_credits', 5),
        '05': ('games_played', 4),
        '06': ('games_won', 4),
        '0B': ('bills_accepted', 4),
        '0C': ('current_credits', 5),
        '15': ('total_ticket_in', 5),
        '16': ('total_ticket_out', 5),
        '17': ('total_electronic_in', 5),
        '18': ('total_electronic_out', 5),
        '1D': ('machine_paid_progressive', 5),
        '1E': ('total_bonus', 5),
        '23': ('total_handpaid_credits', 5),
        '7F': ('weighted_avg_payback', 4),
        'A0': ('total_coin_in', 5),
        'A2': ('non_cashable_in', 5),
        'B8': ('total_coin_out', 5),
        'BA': ('non_cashable_out', 5),
        'FA': ('regular_cashable_keyed', 5),
        'FB': ('restricted_keyed', 5),
        'FC': ('nonrestricted_keyed', 5),
        # Additional common SAS meter codes
        '10': ('total_cancelled_credits_meter', 5),
        '11': ('total_bet_meter', 5),
        '12': ('total_win_meter', 5),
        '13': ('total_in_meter', 5),
        '14': ('total_jackpot_meter', 5),
        '15': ('games_played_meter', 4),
        '16': ('games_won_meter', 4),
        '1A': ('current_credits_meter', 5),
    }

    # Single meter command codes (for individual meter requests)
    SINGLE_METER_CODES = {
        'total_bet': '11',
        'total_win': '12', 
        'total_in': '13',
        'total_jackpot': '14',
        'games_played': '15',
        'games_won': '16',
        'total_cancelled': '10',
        'current_credits': '1A',
        'bills_total': '1E',
    }

    def get_length_by_meter_code(self, meter_code):
        """
        Determine meter value length by code, exactly matching the reference implementation.
        Some meters are 5 bytes, others are 4 bytes.
        """
        five_byte_codes = ["0D", "0E", "0F", "10", "80", "82", "84", "86", "88", "8A", "8C", "8E", 
                          "90", "92", "A0", "A2", "A4", "A6", "A8", "AA", "AC", "AE", "B0", "B8", 
                          "BA", "BC"]
        
        if meter_code.upper() in five_byte_codes:
            return 5
        return 4

    def handle_single_meter_response(self, tdata):
        """
        Parses a SAS meter response using the exact logic from the working reference Yanit_MeterAll function.
        Supports both 2F and AF command types with dynamic code/length parsing.
        """
        print(f"--- Parsing SAS Meter Response: {tdata} ---")
        if len(tdata) < 10:
            print(f"Response too short to be a valid meter block: {tdata}")
            return

        idx = 0
        address = tdata[idx:idx+2]
        idx += 2
        command = tdata[idx:idx+2].upper()
        idx += 2
        length = tdata[idx:idx+2]
        idx += 2
        
        message_length = (int(tdata[4:6], 16) * 2) + 10
        
        if command == "2F":
            game_number = tdata[idx:idx+4]
            idx += 4

        parsed_meters = {}
        received_all_meter = f"{tdata}|"

        def money_fmt(val):
            return f"{val:,.2f} TL"

        print(f"[DEBUG] Entered handle_single_meter_response with command: {command}")

        if command == "2F":
            # Parse as block using reference logic: [code][value]...[code][value]...
            meter_code = "XXXX"
            # Calculate where meter data should end (exclude CRC)
            meter_data_end = message_length - 4  # Subtract 4 for CRC
            
            while len(meter_code) > 0 and idx < meter_data_end:
                if idx + 2 > meter_data_end:
                    break
                    
                meter_code = tdata[idx:idx+2].upper()
                if not meter_code or len(meter_code) < 2:
                    break
                idx += 2
                
                next_length = self.get_length_by_meter_code(meter_code) * 2
                
                if idx + next_length > meter_data_end:
                    print(f"[DEBUG] Would exceed meter data boundary, stopping at code {meter_code}")
                    break
                    
                meter_val = tdata[idx:idx+next_length]
                idx += next_length
                
                print(f"[DEBUG] meter_code={meter_code}, length={next_length//2} bytes, meter_val={meter_val}")
                
                try:
                    # Use decimal interpretation, divide by 10 (not 100) for this machine
                    meter_value = int(meter_val) / 10.0
                    
                    # Store the parsed meter using the same variable names as reference
                    meter_name = self.METER_CODE_MAP.get(meter_code, (meter_code, next_length//2))[0]
                    parsed_meters[meter_name] = meter_value
                    received_all_meter += f"{meter_code}-{meter_val}|"
                    
                    print(f"  {meter_name} ({meter_code}): {money_fmt(meter_value)}")
                    
                except Exception as e:
                    print(f"Meter parse error: {meter_code} {meter_val} {e}")
                    break
            print("--- End of 2F Meter Block ---")
            
        elif command == "AF":
            # Parse AF format exactly like reference implementation
            # Reference shows: MeterCode=Yanit[index:index+2]; index=index+4
            try_count = 0
            
            # Calculate where meter data should end (exclude CRC)
            meter_data_end = message_length - 4  # Subtract 4 for CRC
            
            # Skip initial padding zeros
            while idx < meter_data_end and tdata[idx:idx+2] == "00":
                idx += 2
            
            known_meter_codes = set(self.METER_CODE_MAP.keys())
            
            while try_count < 15 and idx < meter_data_end:
                try_count += 1
                
                # Look for next meter code - scan ahead if needed
                found_meter = False
                original_idx = idx
                
                # Search for next valid meter code within reasonable range
                for search_idx in range(idx, min(idx + 100, meter_data_end), 2):
                    if search_idx + 2 <= meter_data_end:
                        potential_code = tdata[search_idx:search_idx+2].upper()
                        if potential_code in known_meter_codes:
                            print(f"[DEBUG] Found meter code {potential_code} at index {search_idx}")
                            idx = search_idx
                            found_meter = True
                            break
                
                if not found_meter:
                    print(f"[DEBUG] No more meter codes found after index {original_idx}")
                    break
                
                meter_code = tdata[idx:idx+2].upper()
                idx += 4  # Skip meter code + 00 (matches reference: index=index+4)
                
                # Get meter length - exactly like reference  
                if idx + 2 > meter_data_end:
                    print(f"[DEBUG] Not enough data for meter length at index {idx}")
                    break
                meter_length = int(tdata[idx:idx+2], 16)
                idx += 2
                hex_len = meter_length * 2  # MeterLength=MeterLength*2 in reference
                
                # Validate meter length makes sense
                if meter_length == 0 or hex_len == 0:
                    print(f"[DEBUG] Invalid meter length {meter_length} for code {meter_code}")
                    continue  # Skip this meter and continue looking
                
                # Get meter value - exactly like reference
                if idx + hex_len > meter_data_end:
                    print(f"[DEBUG] Meter value would exceed data boundary for code {meter_code}")
                    break
                meter_val = tdata[idx:idx+hex_len]
                idx += hex_len
                
                print(f"[DEBUG] AF meter_code={meter_code}, length={meter_length} bytes, meter_val={meter_val}")
                
                try:
                    # Convert meter values with proper scaling based on meter type
                    if not meter_val:  # Empty meter value
                        print(f"[DEBUG] Empty meter value for code {meter_code}, skipping")
                        continue
                    
                    raw_value = int(meter_val)
                    meter_name = self.METER_CODE_MAP.get(meter_code, (meter_code, meter_length))[0]
                    
                    # Special handling for different meter types
                    if meter_code in ["05", "06"]:  # Games played/won - these are counts, not currency
                        meter_value = raw_value  # No scaling for game counts
                        parsed_meters[meter_name] = meter_value
                        print(f"  {meter_name} ({meter_code}): {meter_value} games")
                        if meter_code == "06":  # Debug info for games won
                            print("MeterCode", meter_code, "MeterLength", meter_length, "MeterVal", meter_val, "MeterValue", meter_value)
                    elif meter_code in ["A0", "B8"]:  # Coin in/out - divide by 100 for proper decimal places
                        # Raw: 000000000089475290 -> 89475290 -> 894752.90 (divide by 100)
                        meter_value = raw_value / 100.0
                        parsed_meters[meter_name] = meter_value
                        print(f"  {meter_name} ({meter_code}): {money_fmt(meter_value)}")
                    else:  # Other currency amounts - divide by 10 based on reference image analysis
                        # Raw: 000000000013187000 -> 13187000 -> 1318700.0 (divide by 10)
                        meter_value = raw_value / 10.0
                        parsed_meters[meter_name] = meter_value
                        print(f"  {meter_name} ({meter_code}): {money_fmt(meter_value)}")
                    
                    received_all_meter += f"{meter_code}-{meter_val}|"
                    
                except Exception as e:
                    print(f"AF Meter parse error: {meter_code} {meter_val} {e}")
                    continue  # Continue to next meter instead of breaking
            print("--- End of AF Meter Block ---")
            
        else:
            print(f"Unknown meter response command: {command}")

        # Check message length like the reference
        if len(tdata) < message_length:
            print("********** METER RECEIVED BUT NOT ACCEPTED! ***************")
            print(f"Expected length: {message_length}, actual: {len(tdata)}")
            return
            
        # Clear waiting flag like the reference
        self.is_waiting_for_meter = False
        print(received_all_meter)
        print("Meter is received")
        
        print(f"[DEBUG] handle_single_meter_response finished. Parsed meters: {parsed_meters}")
        
        # Calculate balance from meters
        if 'total_coin_in' in parsed_meters and 'total_coin_out' in parsed_meters:
            calculated_balance = parsed_meters['total_coin_in'] - parsed_meters['total_coin_out']
            parsed_meters['calculated_balance'] = calculated_balance
            print(f"  calculated_balance: {money_fmt(calculated_balance)} (coin_in - coin_out)")
        
        # Add current credits if available
        if 'current_credits' in parsed_meters:
            print(f"  current_credits: {money_fmt(parsed_meters['current_credits'])}")
        
        # Store parsed meters for API access
        self.last_parsed_meters = parsed_meters
        
        return parsed_meters

    def get_meter(self, isall=0, sender="Unknown", gameid=0):
        """
        Sends a meter request and waits for a response with a simple timeout.
        This version avoids sending rapid, duplicate commands.
        """
        print(f"=== METER: Getting meters (isall={isall}, sender={sender}) ===")
        start_time = datetime.datetime.now()
        self.is_waiting_for_meter = True
        self.meter_response_received = False
        # Send the command once
        self.komut_get_meter(isall, gameid)
        # Wait for a response with a timeout
        timeout_seconds = 5
        while self.is_waiting_for_meter and (datetime.datetime.now() - start_time).total_seconds() < timeout_seconds:
            time.sleep(0.1) # Poll for the response flag every 100ms
        if not self.is_waiting_for_meter:
            print("METER: Success! Meter response received.")
        else:
            # If we're still waiting, it's a timeout
            self.is_waiting_for_meter = False # Ensure the loop terminates
            print(f"METER: Timeout after {timeout_seconds} seconds waiting for meter response.")
        duration = datetime.datetime.now() - start_time
        print(f"=== METER: Process completed in {duration.total_seconds():.2f} seconds ===")

    def run_all_meters(self):
        print("DEBUG: run_all_meters START")
        self.get_meter(isall=0)
        print("DEBUG: run_all_meters END")

    def is_valid_bcd(self, hex_str):
        """Check if a hex string is valid BCD (only 0-9 digits)."""
        return all(c in '0123456789' for c in hex_str) 

    def yanit_para_yukle(self, yanit):
        """
        Handle AFT money load response from the machine.
        SIMPLIFIED to match working code exactly - Fix for over-complex parsing
        
        This mirrors the original Yanit_ParaYukle function that was simple and direct
        """
        # Only process if we're actually waiting for this response
        # CRITICAL: This matches the original Yanit_ParaYukle logic that checked IsWaitingForParaYukle
        if self.is_waiting_for_para_yukle != 1:
            print(f"[MONEY LOAD RESPONSE] ⚠️  Not waiting for AFT response, ignoring...")
            return
        
        try:
            print(f"[MONEY LOAD RESPONSE] ===== AFT TRANSFER RESPONSE =====")
            print(f"[MONEY LOAD RESPONSE] Raw response: {yanit}")
            print(f"[MONEY LOAD RESPONSE] Response length: {len(yanit)} characters")
            
            # Extract status at fixed position (matching working code)
            # CRITICAL: Direct extraction like original - no complex parsing
            transfer_status = yanit[8:10] if len(yanit) >= 10 else "FF"
            
            print(f"[MONEY LOAD RESPONSE] Transfer Status: {transfer_status}")
            
            # CRITICAL: Direct status update (no complex parsing) - matches original exactly
            # In original: Global_ParaYukleme_TransferStatus = transfer_status_code
            old_status = self.global_para_yukleme_transfer_status
            self.global_para_yukleme_transfer_status = transfer_status
            
            print(f"[MONEY LOAD RESPONSE] Status updated: {old_status} → {transfer_status}")
            print(f"[MONEY LOAD RESPONSE] Status Description: {self.get_transfer_status_description(transfer_status)}")
            
            # DON'T clear waiting flag here - let wait loop handle it (CRITICAL FIX)
            # The original working code let the wait loop clear IsWaitingForParaYukle
            print(f"[MONEY LOAD RESPONSE] Waiting flag remains: {self.is_waiting_for_para_yukle} (wait loop will clear it)")
            
        except Exception as e:
            print(f"[MONEY LOAD RESPONSE] ❌ Error: {e}")
            # CRITICAL: Even on error, update status to prevent infinite wait
            self.global_para_yukleme_transfer_status = "FF"
            print(f"[MONEY LOAD RESPONSE] Set error status due to parse error")

    def yanit_aft_registration(self, yanit):
        """
        Handle AFT registration response from the machine.
        This method parses the SAS 73h response and updates registration status.
        
        Args:
            yanit: Hex string response from the machine
        """
        try:
            print(f"[AFT REG RESPONSE] Received AFT registration response: {yanit}")
            print(f"[AFT REG RESPONSE] Response length: {len(yanit)} characters")
            
            if len(yanit) < 8:
                print(f"[AFT REG RESPONSE] Response too short: {len(yanit)} characters")
                return
            
            # Parse response according to SAS protocol
            # Format: Address(2) + Command(2) + Length(2) + RegistrationStatus(2) + AssetNumber(8) + RegistrationKey(40) + POSID(8)
            index = 0
            address = yanit[index:index+2]
            index += 2
            print(f"[AFT REG RESPONSE] Address: {address}")
            
            command = yanit[index:index+2]
            index += 2
            print(f"[AFT REG RESPONSE] Command: {command}")
            
            length_hex = yanit[index:index+2]
            index += 2
            print(f"[AFT REG RESPONSE] Length: {length_hex}")
            
            # Validate command is 73 (AFT registration response)
            if command.upper() != "73":
                print(f"[AFT REG RESPONSE] Unexpected command: {command}, expected 73")
                return
            
            registration_status = yanit[index:index+2] if index + 2 <= len(yanit) else "80"
            index += 2
            print(f"[AFT REG RESPONSE] Registration Status: {registration_status}")
            
            # Decode registration status
            status_descriptions = {
                "00": "Registration Ready",
                "01": "Registered",
                "40": "Registration Pending", 
                "80": "Not Registered"
            }
            status_text = status_descriptions.get(registration_status, f"Unknown status: {registration_status}")
            print(f"[AFT REG RESPONSE] Status Description: {status_text}")
            
            # Parse asset number if available
            if index + 8 <= len(yanit):
                asset_number = yanit[index:index+8]
                index += 8
                print(f"[AFT REG RESPONSE] Asset Number: {asset_number}")
                
                # Convert asset number to decimal (little-endian BCD)
                try:
                    asset_dec = self.read_asset_to_int(asset_number)
                    print(f"[AFT REG RESPONSE] Asset Number (decimal): {asset_dec}")
                    
                    # Store asset number in communicator if available
                    if hasattr(self.communicator, 'asset_number'):
                        self.communicator.asset_number = asset_number
                        self.communicator.decimal_asset_number = asset_dec
                        print(f"[AFT REG RESPONSE] Asset number stored in communicator")
                        
                except Exception as e:
                    print(f"[AFT REG RESPONSE] Error converting asset number: {e}")
            
            # Parse registration key if available
            if index + 40 <= len(yanit):
                registration_key = yanit[index:index+40]
                index += 40
                print(f"[AFT REG RESPONSE] Registration Key: {registration_key}")
            
            # Parse POS ID if available
            if index + 8 <= len(yanit):
                pos_id = yanit[index:index+8]
                print(f"[AFT REG RESPONSE] POS ID: {pos_id}")
            
            # Store registration status
            if hasattr(self, 'aft_registration_status'):
                self.aft_registration_status = registration_status
            else:
                self.aft_registration_status = registration_status
                
            print(f"[AFT REG RESPONSE] Registration processing completed")
            
        except Exception as e:
            print(f"[AFT REG RESPONSE] Error parsing AFT registration response: {e}")
            print(f"[AFT REG RESPONSE] Raw response: {yanit}")

    def read_asset_to_int(self, asset_hex):
        """
        Convert asset number from hex string to integer using little-endian format.
        This matches the reference implementation for asset number conversion.
        
        Args:
            asset_hex: 8-character hex string (e.g., "0000006C")
            
        Returns:
            Integer value of the asset number
        """
        try:
            # Ensure even length
            if len(asset_hex) % 2 != 0:
                asset_hex = "0" + asset_hex
            
            # Reverse byte order (little-endian)
            reversed_hex = ""
            i = len(asset_hex) - 2
            while i >= 0:
                reversed_hex += asset_hex[i:i+2]
                i -= 2
            
            # Convert to integer
            result = int(reversed_hex, 16)
            print(f"[ASSET CONVERT] {asset_hex} -> {reversed_hex} -> {result}")
            return result
            
        except Exception as e:
            print(f"[ASSET CONVERT] Error converting asset number {asset_hex}: {e}")
            return 0

    def _int_to_bcd(self, value, byte_count):
        """
        Convert integer to BCD (Binary Coded Decimal) format.
        
        Args:
            value: Integer value to convert
            byte_count: Number of bytes for the BCD representation
            
        Returns:
            Hex string representation of BCD value
        """
        try:
            # Convert to BCD format (each decimal digit becomes 4 bits)
            bcd_str = f"{value:0{byte_count * 2}d}"  # Pad with zeros
            
            # Convert each pair of digits to hex
            bcd_hex = ""
            for i in range(0, len(bcd_str), 2):
                digit_pair = bcd_str[i:i+2]
                if len(digit_pair) == 1:
                    digit_pair = "0" + digit_pair
                bcd_hex += f"{int(digit_pair):02X}"
            
            print(f"[BCD CONVERT] {value} -> {bcd_str} -> {bcd_hex}")
            return bcd_hex
            
        except Exception as e:
            print(f"[BCD CONVERT] Error converting {value} to BCD: {e}")
            return "00" * byte_count 

    def komut_unlock_machine(self):
        """
        Send AFT unlock command to the gaming machine.
        This sends SAS command 74h with unlock code to enable AFT transfers.
        """
        print(f"[AFT UNLOCK] Attempting to unlock machine for AFT transfers")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Get the correct asset number from the communicator
        asset_number = "0000006C"  # Default to known asset number (108 decimal)
        if hasattr(self.communicator, 'asset_number') and self.communicator.asset_number:
            asset_number = self.communicator.asset_number.upper()
        elif hasattr(self.communicator, 'asset_number_hex') and self.communicator.asset_number_hex:
            asset_number = self.communicator.asset_number_hex.upper()
        
        print(f"[AFT UNLOCK] Using asset number: {asset_number}")
        
        # AFT unlock/lock command: 74h 
        # IMPORTANT: The 74h command is actually "AFT Lock" command, not unlock!
        # To UNLOCK, we need to send lock code 00 (no locks)
        # To LOCK, we would send specific lock codes like FF
        
        # Format: Address + 74h + AssetNumber(4 bytes) + LockCode + TransferCondition + LockTimeout
        # LockCode 00 = No locks (unlock all)
        # TransferCondition 00 = No transfer restrictions  
        # LockTimeout 0000 = No timeout
        
        print(f"[AFT UNLOCK] Attempting to clear all locks (unlock)")
        command = f"{sas_address}74{asset_number}00000000"
        command_crc = get_crc(command)
        
        print(f"[AFT UNLOCK] Sending unlock command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("AFTUnlock", command_crc, 1)
            print(f"[AFT UNLOCK] Unlock command result: {result}")
            
            # Wait a moment for the machine to process the unlock
            import time
            time.sleep(0.5)
            
            # Try additional unlock approaches if the first one doesn't work
            print(f"[AFT UNLOCK] Trying alternative unlock approaches...")
            
            # Approach 2: Some machines need a specific unlock sequence
            # Try with transfer condition FF (all transfers allowed)
            command2 = f"{sas_address}74{asset_number}00FF0000"
            command2_crc = get_crc(command2)
            print(f"[AFT UNLOCK] Sending alternative unlock: {command2_crc}")
            result2 = self.communicator.sas_send_command_with_queue("AFTUnlock2", command2_crc, 1)
            print(f"[AFT UNLOCK] Alternative unlock result: {result2}")
            
            return result
        except Exception as e:
            print(f"[AFT UNLOCK] Error sending unlock command: {e}")
            raise

    def check_aft_status(self):
        """
        Check if the machine is ready for AFT transfers by querying status.
        Returns True if ready, False if locked or unavailable.
        
        IMPORTANT: SAS Protocol Lock Status Values:
        - FF = NOT LOCKED (machine is available)
        - 40 = LOCK PENDING 
        - 00 = LOCKED (machine is locked)
        """
        print(f"[AFT STATUS CHECK] Checking machine AFT status")
        
        # Query balance to get AFT status
        self.komut_bakiye_sorgulama("aft_status_check", False, "status_check")
        
        # Wait a moment for response
        import time
        time.sleep(1)
        
        # Check the last balance response for status indicators
        if hasattr(self.communicator, 'last_game_lock_status'):
            lock_status = self.communicator.last_game_lock_status
            aft_status = self.communicator.last_aft_status
            
            print(f"[AFT STATUS CHECK] Current Lock Status: {lock_status}")
            print(f"[AFT STATUS CHECK] Current AFT Status: {aft_status}")
            
            # CORRECTED: Analyze the status codes according to SAS protocol
            if lock_status == "FF":
                print(f"[AFT STATUS CHECK] ✅ Machine is NOT LOCKED (FF = available for AFT)")
                return True
            elif lock_status == "00":
                print(f"[AFT STATUS CHECK] ❌ Machine is LOCKED (00 = locked state)")
                return False
            elif lock_status == "40":
                print(f"[AFT STATUS CHECK] ⏳ Machine lock PENDING (40 = transitioning)")
                return False
            else:
                print(f"[AFT STATUS CHECK] ⚠️  Unknown lock status: {lock_status}")
                # For unknown status, check if AFT appears functional
                if aft_status in ["B0", "A0", "90", "80"]:  # Common AFT states
                    print(f"[AFT STATUS CHECK] ⚠️  Unknown lock but AFT may still work")
                    return True
                else:
                    return False
        else:
            print(f"[AFT STATUS CHECK] ⚠️  No status information available")
            return False

    def komut_advanced_unlock(self):
        """
        Advanced unlock method that tries multiple approaches to unlock the machine.
        This method addresses common lock conditions that might prevent AFT transfers.
        """
        print(f"[ADVANCED UNLOCK] Starting comprehensive unlock sequence")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        asset_number = "0000006C"
        if hasattr(self.communicator, 'asset_number') and self.communicator.asset_number:
            asset_number = self.communicator.asset_number.upper()
        
        print(f"[ADVANCED UNLOCK] Using asset number: {asset_number}")
        
        try:
            # Step 1: Clear all game locks (00 = no locks)
            print(f"[ADVANCED UNLOCK] Step 1: Clear all game locks")
            cmd1 = f"{sas_address}74{asset_number}00000000"
            result1 = self.communicator.sas_send_command_with_queue("UnlockStep1", get_crc(cmd1), 1)
            print(f"[ADVANCED UNLOCK] Clear locks result: {result1}")
            
            import time
            time.sleep(0.5)
            
            # Step 2: Enable all transfer types (FF = all transfers allowed)
            print(f"[ADVANCED UNLOCK] Step 2: Enable all transfer types")  
            cmd2 = f"{sas_address}74{asset_number}00FF0000"
            result2 = self.communicator.sas_send_command_with_queue("UnlockStep2", get_crc(cmd2), 1)
            print(f"[ADVANCED UNLOCK] Enable transfers result: {result2}")
            
            time.sleep(0.5)
            
            # Step 3: Try with extended timeout to allow machine processing
            print(f"[ADVANCED UNLOCK] Step 3: Set extended unlock timeout")
            cmd3 = f"{sas_address}74{asset_number}00FFFF00"  # Extended timeout
            result3 = self.communicator.sas_send_command_with_queue("UnlockStep3", get_crc(cmd3), 1)
            print(f"[ADVANCED UNLOCK] Extended timeout result: {result3}")
            
            time.sleep(1)  # Give more time for processing
            
            # Step 4: Query status to confirm unlock
            print(f"[ADVANCED UNLOCK] Step 4: Verify unlock status")
            self.komut_bakiye_sorgulama("advanced_unlock_verify", False, "unlock_verification")
            
            time.sleep(1)
            
            # Check results
            if hasattr(self.communicator, 'last_game_lock_status'):
                lock_status = self.communicator.last_game_lock_status
                aft_status = getattr(self.communicator, 'last_aft_status', 'FF')
                
                if lock_status == "00":
                    print(f"[ADVANCED UNLOCK] ✅ SUCCESS: Machine unlocked!")
                    return True
                elif lock_status == "FF":
                    print(f"[ADVANCED UNLOCK] ⚠️  Machine reports all locks (FF) - checking AFT functionality")
                    # In test/simulation mode, machine may report FF but still work
                    # Check if we can get successful AFT responses
                    if aft_status in ["B0", "A0", "90"]:
                        print(f"[ADVANCED UNLOCK] ✅ AFT appears functional despite lock status - proceeding")
                        return True
                    else:
                        print(f"[ADVANCED UNLOCK] ❌ FAILED: Machine not responding to AFT")
                        return False
                else:
                    print(f"[ADVANCED UNLOCK] ⚠️  PARTIAL: Lock status improved to {lock_status}")
                    return True
            else:
                print(f"[ADVANCED UNLOCK] ⚠️  Cannot verify - no status available")
                return None
                
        except Exception as e:
            print(f"[ADVANCED UNLOCK] Error in unlock sequence: {e}")
            return False

    def komut_machine_enable(self):
        """
        Enable the machine using SAS enable command.
        Sometimes machines need to be enabled before they can be unlocked.
        """
        print(f"[MACHINE ENABLE] Enabling machine before unlock")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Enable command: 8Eh
        command = f"{sas_address}8E"
        command_crc = get_crc(command)
        
        print(f"[MACHINE ENABLE] Sending enable command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("MachineEnable", command_crc, 1)
            print(f"[MACHINE ENABLE] Enable result: {result}")
            return result
        except Exception as e:
            print(f"[MACHINE ENABLE] Error enabling machine: {e}")
            return False

    def komut_clear_host_controls(self):
        """
        Clear host controls that might be preventing AFT operations.
        Some machines have host-controlled lockouts that need to be cleared.
        """
        print(f"[CLEAR HOST CONTROLS] Clearing host-controlled lockouts")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Clear host controls: 85h (Clear host control)
        command = f"{sas_address}85"
        command_crc = get_crc(command)
        
        print(f"[CLEAR HOST CONTROLS] Sending clear command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("ClearHostControls", command_crc, 1)
            print(f"[CLEAR HOST CONTROLS] Clear result: {result}")
            return result
        except Exception as e:
            print(f"[CLEAR HOST CONTROLS] Error clearing controls: {e}")
            return False

    def komut_get_machine_status(self):
        """
        Get detailed machine status to understand why it won't unlock.
        This uses SAS command 02h to get general status information.
        """
        print(f"[MACHINE STATUS] Getting detailed machine status")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # General status query: 02h
        command = f"{sas_address}02"
        command_crc = get_crc(command)
        
        print(f"[MACHINE STATUS] Sending status query: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("MachineStatus", command_crc, 1)
            print(f"[MACHINE STATUS] Status query result: {result}")
            return result
        except Exception as e:
            print(f"[MACHINE STATUS] Error getting status: {e}")
            return False

    def komut_get_gaming_machine_info(self):
        """
        Get gaming machine information including capabilities and restrictions.
        This uses SAS command 01h to get machine identification.
        """
        print(f"[MACHINE INFO] Getting gaming machine information")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Machine info query: 01h
        command = f"{sas_address}01"
        command_crc = get_crc(command)
        
        print(f"[MACHINE INFO] Sending info query: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("MachineInfo", command_crc, 1)
            print(f"[MACHINE INFO] Info query result: {result}")
            return result
        except Exception as e:
            print(f"[MACHINE INFO] Error getting info: {e}")
            return False

    def komut_reserve_machine(self):
        """
        Reserve the machine using SAS command.
        When a machine is "reserved", it won't accept AFT transfers from other systems.
        This uses SAS command 8C to reserve the machine.
        """
        print(f"[RESERVE MACHINE] Reserving machine for exclusive access")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Reserve machine command: 8Ch
        command = f"{sas_address}8C"
        command_crc = get_crc(command)
        
        print(f"[RESERVE MACHINE] Sending reserve machine command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("ReserveMachine", command_crc, 1)
            print(f"[RESERVE MACHINE] Reserve machine result: {result}")
            return result
        except Exception as e:
            print(f"[RESERVE MACHINE] Error reserving machine: {e}")
            return False

    def komut_clear_machine_reservation(self):
        """
        Clear machine reservation status using SAS command.
        When a machine is "reserved", it won't accept AFT transfers until cleared.
        This uses SAS command 8F to clear the reservation.
        """
        print(f"[CLEAR RESERVATION] Clearing machine reservation status")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Clear reservation command: 8Fh
        command = f"{sas_address}8F"
        command_crc = get_crc(command)
        
        print(f"[CLEAR RESERVATION] Sending clear reservation command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("ClearReservation", command_crc, 1)
            print(f"[CLEAR RESERVATION] Clear reservation result: {result}")
            return result
        except Exception as e:
            print(f"[CLEAR RESERVATION] Error clearing reservation: {e}")
            return False

    def komut_disable_machine(self):
        """
        Disable the machine using SAS command 8Dh.
        Sometimes needed before clearing reservation.
        """
        print(f"[MACHINE DISABLE] Disabling machine")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        # Disable command: 8Dh
        command = f"{sas_address}8D"
        command_crc = get_crc(command)
        
        print(f"[MACHINE DISABLE] Sending disable command: {command_crc}")
        
        try:
            result = self.communicator.sas_send_command_with_queue("MachineDisable", command_crc, 1)
            print(f"[MACHINE DISABLE] Disable result: {result}")
            return result
        except Exception as e:
            print(f"[MACHINE DISABLE] Error disabling machine: {e}")
            return False

    def komut_clear_reservation_sequence(self):
        """
        Complete sequence to clear machine reservation and enable AFT.
        This tries multiple approaches to clear the reserved status.
        """
        print(f"[RESERVATION SEQUENCE] Starting complete reservation clearing sequence")
        
        try:
            # Step 1: Disable machine first
            print(f"[RESERVATION SEQUENCE] Step 1: Disable machine")
            disable_result = self.komut_disable_machine()
            print(f"[RESERVATION SEQUENCE] Disable result: {disable_result}")
            
            import time
            time.sleep(1)
            
            # Step 2: Clear reservation
            print(f"[RESERVATION SEQUENCE] Step 2: Clear reservation")
            clear_result = self.komut_clear_machine_reservation()
            print(f"[RESERVATION SEQUENCE] Clear result: {clear_result}")
            
            time.sleep(1)
            
            # Step 3: Enable machine
            print(f"[RESERVATION SEQUENCE] Step 3: Enable machine")
            enable_result = self.komut_machine_enable()
            print(f"[RESERVATION SEQUENCE] Enable result: {enable_result}")
            
            time.sleep(1)
            
            # Step 4: Clear any remaining host controls
            print(f"[RESERVATION SEQUENCE] Step 4: Clear host controls")
            host_clear_result = self.komut_clear_host_controls()
            print(f"[RESERVATION SEQUENCE] Host clear result: {host_clear_result}")
            
            time.sleep(1)
            
            # Step 5: Try unlock after clearing reservation
            print(f"[RESERVATION SEQUENCE] Step 5: Unlock machine")
            unlock_result = self.komut_unlock_machine()
            print(f"[RESERVATION SEQUENCE] Unlock result: {unlock_result}")
            
            time.sleep(2)
            
            # Step 6: Verify status
            print(f"[RESERVATION SEQUENCE] Step 6: Verify machine status")
            self.komut_bakiye_sorgulama("reservation_clear_verify", False, "reservation_verification")
            
            time.sleep(2)
            
            # Check results
            if hasattr(self.communicator, 'last_game_lock_status'):
                lock_status = self.communicator.last_game_lock_status
                if lock_status == "00":
                    print(f"[RESERVATION SEQUENCE] ✅ SUCCESS: Machine reservation cleared and unlocked!")
                    return True
                elif lock_status != "FF":
                    print(f"[RESERVATION SEQUENCE] ⚠️  PARTIAL SUCCESS: Lock status improved to {lock_status}")
                    return True
                else:
                    print(f"[RESERVATION SEQUENCE] ❌ FAILED: Machine still shows reservation/locks ({lock_status})")
                    return False
            else:
                print(f"[RESERVATION SEQUENCE] ⚠️  Cannot verify - no status available")
                return None
                
        except Exception as e:
            print(f"[RESERVATION SEQUENCE] Error in reservation clearing sequence: {e}")
            return False

    def decode_aft_status(self, aft_status_hex):
        """
        Decode the AFT status byte to understand specific lock conditions.
        AFT Status B0 = 10110000 binary
        """
        try:
            status_int = int(aft_status_hex, 16)
            print(f"[AFT STATUS DECODE] AFT Status: {aft_status_hex} = {status_int} = {bin(status_int)}")
            
            # Decode individual bits (based on SAS AFT status specification)
            bit_meanings = {
                0: "AFT registered",
                1: "AFT enabled", 
                2: "AFT transfer pending",
                3: "AFT transfer in progress",
                4: "Machine cashout mode",
                5: "Host cashout enabled",
                6: "AFT bonus mode",
                7: "Machine locked"
            }
            
            print(f"[AFT STATUS DECODE] Status breakdown:")
            for bit, meaning in bit_meanings.items():
                bit_set = (status_int >> bit) & 1
                status_text = "SET" if bit_set else "CLEAR"
                print(f"[AFT STATUS DECODE]   Bit {bit} ({meaning}): {status_text}")
                
            return status_int
        except Exception as e:
            print(f"[AFT STATUS DECODE] Error decoding status: {e}")
            return None

    def decode_lock_status(self, lock_status_hex):
        """
        Decode the game lock status according to SAS protocol specification.
        
        CORRECT SAS Protocol Game Lock Status Values:
        - FF = NOT LOCKED (machine available for normal operation)
        - 00 = LOCKED (machine locked for AFT transfers)  
        - 40 = LOCK PENDING (lock request pending)
        
        This is NOT a bit field - it's a specific status code!
        """
        try:
            status_hex = lock_status_hex.upper()
            print(f"[LOCK STATUS DECODE] Game Lock Status: {status_hex}")
            
            # Decode according to SAS protocol specification (Section 8.2)
            if status_hex == "FF":
                print(f"[LOCK STATUS DECODE] ✅ NOT LOCKED - Machine available for normal operation")
                return "NOT_LOCKED"
            elif status_hex == "00":
                print(f"[LOCK STATUS DECODE] 🔒 LOCKED - Machine locked for AFT transfers")
                return "LOCKED"
            elif status_hex == "40":
                print(f"[LOCK STATUS DECODE] ⏳ LOCK PENDING - Lock request pending")
                return "LOCK_PENDING"
            else:
                print(f"[LOCK STATUS DECODE] ⚠️  UNKNOWN STATUS: {status_hex} (not in SAS specification)")
                return f"UNKNOWN_{status_hex}"
                
        except Exception as e:
            print(f"[LOCK STATUS DECODE] Error decoding lock status: {e}")
            return None 

    def komut_aft_lock_machine(self, timeout_seconds=30):
        """
        Lock the machine for AFT transfers using SAS 74h command with lock code 00.
        This implements the proper AFT Game Lock sequence from the SAS protocol.
        
        Returns:
            True if lock successful, False if failed
        """
        try:
            print(f"[AFT LOCK] Initiating AFT Game Lock (timeout: {timeout_seconds}s)")
            
            # Get asset number
            asset_number = getattr(self.communicator, 'asset_number', '0000006C')
            if not asset_number or asset_number == '01':  # Don't use SAS address as asset number
                asset_number = '0000006C'
            
            print(f"[AFT LOCK] Using asset number: {asset_number}")
            
            # Build AFT lock command (SAS 74h with lock code 00)
            sas_address = getattr(self.communicator, 'sas_address', '01')
            command_code = '74'
            
            # FIXED: AFT Game Lock command format (no length field needed)
            # Format: Address + 74h + AssetNumber + LockCode + TransferCondition + LockTimeout
            command_body = asset_number  # Asset number (4 bytes)
            command_body += '00'         # Lock code: 00 = Request lock
            command_body += '01'         # Transfer condition: 01 = AFT transfers only  
            command_body += f'{timeout_seconds:02X}'  # Lock timeout in seconds (1 byte)
            
            # Build complete command (no length field for 74h command)
            complete_command_no_crc = sas_address + command_code + command_body
            complete_command = get_crc(complete_command_no_crc)
            
            print(f"[AFT LOCK] Sending AFT lock command: {complete_command}")
            print(f"[AFT LOCK] Command breakdown:")
            print(f"  Header: {sas_address}{command_code}")
            print(f"  Asset Number: {asset_number}")
            print(f"  Lock Code: 00 (request lock)")
            print(f"  Transfer Condition: 01 (AFT only)")
            print(f"  Timeout: {timeout_seconds}s")
            
            # Send the lock command
            result = self.communicator.sas_send_command_with_queue("AFTLock", complete_command, 1)
            print(f"[AFT LOCK] Lock command result: {result}")
            
            # Wait for lock to be established
            import time
            time.sleep(2)
            
            # Verify lock status
            print(f"[AFT LOCK] Verifying lock status...")
            self.komut_bakiye_sorgulama("aft_lock_verify", False, "aft_lock_verification")
            
            time.sleep(1)
            
            # Check if lock was successful
            if hasattr(self.communicator, 'last_game_lock_status'):
                lock_status = self.communicator.last_game_lock_status
                print(f"[AFT LOCK] Lock verification - Game Lock Status: {lock_status}")
                
                if lock_status == '00':
                    print(f"[AFT LOCK] ✅ SUCCESS: Machine locked for AFT transfers")
                    return True
                elif lock_status == '40':
                    print(f"[AFT LOCK] ⏳ PENDING: Lock request pending, may need more time")
                    return True  # Consider pending as success for now
                else:
                    print(f"[AFT LOCK] ❌ FAILED: Lock status {lock_status} - {self.decode_lock_status(lock_status)}")
                    return False
            else:
                print(f"[AFT LOCK] ⚠️  Cannot verify lock status - no response available")
                return None
                
        except Exception as e:
            print(f"[AFT LOCK] Error locking machine: {e}")
            return False

    def komut_aft_unlock_machine(self):
        """
        Unlock the machine after AFT transfers using SAS 74h command with lock code FF.
        This implements the proper AFT Game Unlock sequence from the SAS protocol.
        
        Returns:
            True if unlock successful, False if failed
        """
        try:
            print(f"[AFT UNLOCK] Initiating AFT Game Unlock")
            
            # Get asset number
            asset_number = getattr(self.communicator, 'asset_number', '0000006C')
            if not asset_number or asset_number == '01':
                asset_number = '0000006C'
            
            print(f"[AFT UNLOCK] Using asset number: {asset_number}")
            
            # Build AFT unlock command (SAS 74h with lock code FF)
            sas_address = getattr(self.communicator, 'sas_address', '01')
            command_code = '74'
            
            # FIXED: AFT Game Lock command format (no length field needed)
            # Format: Address + 74h + AssetNumber + LockCode + TransferCondition + LockTimeout
            command_body = asset_number  # Asset number (4 bytes)
            command_body += 'FF'         # Lock code: FF = Request unlock/status only
            command_body += '00'         # Transfer condition (ignored for unlock)
            command_body += '00'         # Lock timeout (ignored for unlock)
            
            # Build complete command (no length field for 74h command)
            complete_command_no_crc = sas_address + command_code + command_body
            complete_command = get_crc(complete_command_no_crc)
            
            print(f"[AFT UNLOCK] Sending AFT unlock command: {complete_command}")
            print(f"[AFT UNLOCK] Command breakdown:")
            print(f"  Header: {sas_address}{command_code}")
            print(f"  Asset Number: {asset_number}")
            print(f"  Lock Code: FF (request unlock)")
            print(f"  Transfer Condition: 00")
            print(f"  Timeout: 00")
            
            # Send the unlock command
            result = self.communicator.sas_send_command_with_queue("AFTUnlock", complete_command, 1)
            print(f"[AFT UNLOCK] Unlock command result: {result}")
            
            # Wait for unlock to be processed
            import time
            time.sleep(2)
            
            # Verify unlock status
            print(f"[AFT UNLOCK] Verifying unlock status...")
            self.komut_bakiye_sorgulama("aft_unlock_verify", False, "aft_unlock_verification")
            
            time.sleep(1)
            
            # Check if unlock was successful
            if hasattr(self.communicator, 'last_game_lock_status'):
                lock_status = self.communicator.last_game_lock_status
                aft_status = getattr(self.communicator, 'last_aft_status', 'FF')
                
                print(f"[AFT UNLOCK] Unlock verification:")
                print(f"  Game Lock Status: {lock_status} - {self.decode_lock_status(lock_status)}")
                print(f"  AFT Status: {aft_status} - {self.decode_aft_status(aft_status)}")
                
                if lock_status == 'FF':
                    print(f"[AFT UNLOCK] ✅ SUCCESS: Machine unlocked successfully")
                    return True
                elif lock_status in ['00', '40']:
                    print(f"[AFT UNLOCK] ⚠️  PARTIAL: Machine still locked, may need additional unlock commands")
                    # Try the cancel AFT transfer command as backup
                    print(f"[AFT UNLOCK] Attempting AFT cancel as backup unlock method...")
                    cancel_result = self.komut_cancel_aft_transfer()
                    return cancel_result
                else:
                    print(f"[AFT UNLOCK] ❌ FAILED: Unexpected lock status {lock_status}")
                    return False
            else:
                print(f"[AFT UNLOCK] ⚠️  Cannot verify unlock status - no response available")
                return None
                
        except Exception as e:
            print(f"[AFT UNLOCK] Error unlocking machine: {e}")
            return False

    def komut_para_yukle_with_auto_lock(self, customerbalance=0.0, customerpromo=0.0, transfertype=10, 
                                       assetnumber=None, registrationkey=None, transactionid=None):
        """
        Enhanced AFT Transfer with automatic lock/unlock management.
        This is the recommended method for AFT transfers as it handles the complete workflow.
        
        Returns:
            Transaction ID if successful, None if failed
        """
        try:
            print(f"[AFT AUTO] Starting enhanced AFT transfer with auto lock/unlock")
            print(f"[AFT AUTO] Amount: ${customerbalance}, Promo: ${customerpromo}")
            
            # Step 1: Check current machine status
            print(f"[AFT AUTO] Step 1: Checking current machine status...")
            self.komut_bakiye_sorgulama("aft_pre_check", False, "aft_pre_transfer_check")
            
            import time
            time.sleep(2)
            
            # Check if machine is already locked or has issues
            if hasattr(self.communicator, 'last_game_lock_status'):
                current_lock_status = self.communicator.last_game_lock_status
                current_aft_status = getattr(self.communicator, 'last_aft_status', 'FF')
                
                print(f"[AFT AUTO] Current status:")
                print(f"  Game Lock: {current_lock_status} - {self.decode_lock_status(current_lock_status)}")
                print(f"  AFT Status: {current_aft_status} - {self.decode_aft_status(current_aft_status)}")
                
                # If machine is in a problematic AFT state, try to clear it first
                if current_aft_status in ['B0', 'C0', 'C1', 'C2']:
                    print(f"[AFT AUTO] Machine in AFT pending state, clearing first...")
                    self.komut_cancel_aft_transfer()
                    time.sleep(2)
            
            # Step 2: Lock machine for AFT transfer
            print(f"[AFT AUTO] Step 2: Locking machine for AFT transfer...")
            lock_result = self.komut_aft_lock_machine(timeout_seconds=60)
            
            if lock_result is False:
                print(f"[AFT AUTO] ❌ FAILED: Could not lock machine for AFT transfer")
                return None
            elif lock_result is None:
                print(f"[AFT AUTO] ⚠️  WARNING: Lock status unclear, proceeding with caution...")
            else:
                print(f"[AFT AUTO] ✅ Machine locked successfully")
            
            # Step 3: Perform the AFT transfer
            print(f"[AFT AUTO] Step 3: Performing AFT transfer...")
            transaction_id = self.komut_para_yukle(
                customerbalance=customerbalance,
                customerpromo=customerpromo,
                transfertype=transfertype,
                assetnumber=assetnumber,
                registrationkey=registrationkey,
                transactionid=transactionid
            )
            
            if transaction_id is None:
                print(f"[AFT AUTO] ❌ FAILED: AFT transfer command failed")
                # Still try to unlock the machine
                print(f"[AFT AUTO] Attempting to unlock machine after failed transfer...")
                self.komut_aft_unlock_machine()
                return None
            
            print(f"[AFT AUTO] AFT transfer command sent successfully, transaction ID: {transaction_id}")
            
            # Step 4: Wait for transfer completion
            print(f"[AFT AUTO] Step 4: Waiting for transfer completion...")
            # Note: The wait logic is handled by the calling code using wait_for_para_yukle_completion
            
            return transaction_id
            
        except Exception as e:
            print(f"[AFT AUTO] Error in enhanced AFT transfer: {e}")
            # Try to unlock machine on error
            try:
                print(f"[AFT AUTO] Attempting to unlock machine after error...")
                self.komut_aft_unlock_machine()
            except:
                pass
            return None

    def komut_complete_aft_workflow(self, customerbalance=0.0, customerpromo=0.0):
        """
        Complete AFT workflow with automatic lock/unlock and proper error handling.
        This is the highest-level method that handles the entire AFT process.
        
        Returns:
            dict with 'success', 'transaction_id', 'final_balance', and 'message' keys
        """
        result = {
            'success': False,
            'transaction_id': None,
            'final_balance': 0.0,
            'message': 'Unknown error'
        }
        
        try:
            print(f"[AFT WORKFLOW] Starting complete AFT workflow")
            print(f"[AFT WORKFLOW] Transfer amount: ${customerbalance}")
            
            # Step 1: Enhanced AFT transfer with auto-lock
            transaction_id = self.komut_para_yukle_with_auto_lock(
                customerbalance=customerbalance,
                customerpromo=customerpromo
            )
            
            if transaction_id is None:
                result['message'] = 'AFT transfer initiation failed'
                return result
            
            result['transaction_id'] = transaction_id
            
            # Step 2: Wait for transfer completion (async)
            print(f"[AFT WORKFLOW] Waiting for transfer completion...")
            # Note: This should be called with await from async context
            # For now, we'll return the transaction ID and let the caller handle the wait
            
            result['success'] = True
            result['message'] = 'AFT transfer initiated successfully'
            return result
            
        except Exception as e:
            print(f"[AFT WORKFLOW] Error in complete AFT workflow: {e}")
            result['message'] = f'AFT workflow error: {str(e)}'
            return result

    async def komut_complete_aft_workflow_async(self, customerbalance=0.0, customerpromo=0.0):
        """
        Async version of complete AFT workflow that handles the entire process including waiting.
        
        Returns:
            dict with 'success', 'transaction_id', 'final_balance', and 'message' keys
        """
        result = {
            'success': False,
            'transaction_id': None,
            'final_balance': 0.0,
            'message': 'Unknown error'
        }
        
        try:
            print(f"[AFT WORKFLOW ASYNC] Starting complete async AFT workflow")
            print(f"[AFT WORKFLOW ASYNC] Transfer amount: ${customerbalance}")
            
            # Step 1: Enhanced AFT transfer with auto-lock
            transaction_id = self.komut_para_yukle_with_auto_lock(
                customerbalance=customerbalance,
                customerpromo=customerpromo
            )
            
            if transaction_id is None:
                result['message'] = 'AFT transfer initiation failed'
                return result
            
            result['transaction_id'] = transaction_id
            
            # Step 2: Wait for transfer completion
            print(f"[AFT WORKFLOW ASYNC] Waiting for transfer completion...")
            transfer_result = await self.wait_for_para_yukle_completion(timeout=15)
            
            if transfer_result is True:
                print(f"[AFT WORKFLOW ASYNC] ✅ Transfer completed successfully")
                result['success'] = True
                result['message'] = 'AFT transfer completed successfully'
            elif transfer_result is False:
                print(f"[AFT WORKFLOW ASYNC] ❌ Transfer failed")
                result['message'] = f'AFT transfer failed with status: {self.global_para_yukleme_transfer_status}'
            else:
                print(f"[AFT WORKFLOW ASYNC] ⏰ Transfer timed out")
                result['message'] = 'AFT transfer timed out'
            
            # Step 3: Unlock machine
            print(f"[AFT WORKFLOW ASYNC] Unlocking machine...")
            unlock_result = self.komut_aft_unlock_machine()
            
            if unlock_result:
                print(f"[AFT WORKFLOW ASYNC] ✅ Machine unlocked successfully")
            else:
                print(f"[AFT WORKFLOW ASYNC] ⚠️  Machine unlock may have failed")
            
            # Step 4: Get final balance
            print(f"[AFT WORKFLOW ASYNC] Querying final balance...")
            self.komut_bakiye_sorgulama("aft_final_balance", False, "aft_workflow_final_balance")
            
            # Wait for balance response
            balance_result = await self.wait_for_bakiye_sorgulama_completion(timeout=5)
            
            if balance_result:
                result['final_balance'] = self.yanit_bakiye_tutar
                print(f"[AFT WORKFLOW ASYNC] Final balance: ${result['final_balance']}")
            else:
                print(f"[AFT WORKFLOW ASYNC] Could not retrieve final balance")
            
            return result
            
        except Exception as e:
            print(f"[AFT WORKFLOW ASYNC] Error in async AFT workflow: {e}")
            result['message'] = f'AFT workflow error: {str(e)}'
            
            # Try to unlock machine on error
            try:
                print(f"[AFT WORKFLOW ASYNC] Attempting emergency unlock...")
                self.komut_aft_unlock_machine()
            except:
                pass
                
            return result