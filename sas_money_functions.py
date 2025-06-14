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
        """
        start = time.time()
        self.is_waiting_for_para_yukle = 1
        
        print(f"[AFT WAIT] Starting AFT money load wait (timeout={timeout}s)")
        print(f"[AFT WAIT] Initial status: {self.global_para_yukleme_transfer_status}")
        
        while time.time() - start < timeout:
            # Add a small delay before checking status to allow background thread to update
            await asyncio.sleep(0.1)
            
            status = self.global_para_yukleme_transfer_status
            elapsed = time.time() - start
            
            print(f"[AFT WAIT] {elapsed:.1f}s - Current status: {status}")
            
            if status == "00":  # Success
                self.is_waiting_for_para_yukle = 0
                print(f"[AFT WAIT] SUCCESS after {elapsed:.2f}s")
                return True
            elif status in ("84", "87", "81"):  # Error codes (removed "40" from here)
                self.is_waiting_for_para_yukle = 0
                print(f"[AFT WAIT] FAILED after {elapsed:.2f}s with status: {status}")
                return False
            elif status == "40":  # Transfer pending - keep waiting
                print(f"[AFT WAIT] Transfer pending, continuing to wait...")
                pass
            elif status is None:
                print(f"[AFT WAIT] No response yet, waiting...")
                pass
            else:
                print(f"[AFT WAIT] Unknown status: {status}")
                
            # Check every 500ms instead of immediately looping
            await asyncio.sleep(0.4)  # Total 0.5s with the 0.1s above
            
        # Timeout
        self.is_waiting_for_para_yukle = 0
        print(f"[AFT WAIT] TIMEOUT after {timeout}s - no response from machine")
        print(f"[AFT WAIT] Final status: {self.global_para_yukleme_transfer_status}")
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
            "81": "Transaction ID not unique",
            "84": "Transfer amount exceeds machine limit", 
            "87": "Gaming machine unable to accept transfers (door open, tilt, etc.)",
            "80": "Machine not registered for AFT",
            "82": "Registration key mismatch",
            "83": "No POS ID configured"
        }
        return status_descriptions.get(status_code, f"Unknown status: {status_code}")

    def komut_cancel_aft_transfer(self):
        command = "017201800BB4"
        self.communicator.sas_send_command_with_queue("CancelAFT", command, 1)

    def komut_aft_registration(self, assetnumber, registrationkey, posid):
        """
        Perform AFT registration with the gaming machine.
        This implements the proper two-step AFT registration process:
        1. Initialize registration (code 00)
        2. Complete registration (code 01) with asset number, key, and POS ID
        
        Args:
            assetnumber: 8-character hex asset number (e.g., "0000006C")
            registrationkey: 40-character hex registration key
            posid: POS ID string (will be converted to hex)
        
        Returns:
            Result of the registration command
        """
        print(f"[AFT REGISTRATION] Starting AFT registration process")
        print(f"[AFT REGISTRATION]   Asset Number: {assetnumber}")
        print(f"[AFT REGISTRATION]   Registration Key: {registrationkey}")
        print(f"[AFT REGISTRATION]   POS ID: {posid}")
        
        sas_address = getattr(self.communicator, 'sas_address', '01')
        
        try:
            # Step 1: Initialize registration (code 00)
            print(f"[AFT REGISTRATION] Step 1: Initialize registration")
            init_command = f"{sas_address}7301FF"  # 73h command, length 01, code FF (query status)
            init_command_crc = get_crc(init_command)
            print(f"[AFT REGISTRATION] Sending init command: {init_command_crc}")
            
            result1 = self.communicator.sas_send_command_with_queue("AFTRegInit", init_command_crc, 1)
            print(f"[AFT REGISTRATION] Init command result: {result1}")
            
            # Wait a moment for the machine to process
            import time
            time.sleep(0.5)
            
            # Step 2: Complete registration (code 01)
            print(f"[AFT REGISTRATION] Step 2: Complete registration")
            
            # Convert POS ID to hex (pad to 8 characters)
            posid_hex = ''.join(f"{ord(c):02x}" for c in posid.ljust(4, '\x00')[:4])
            print(f"[AFT REGISTRATION] POS ID hex: {posid_hex}")
            
            # Construct complete registration command
            # Format: Address + 73h + Length + Code(01) + AssetNumber(8) + RegistrationKey(40) + POSID(8)
            command_data = f"01{assetnumber}{registrationkey}{posid_hex}"
            # Calculate correct length: data length in bytes
            data_length = len(command_data) // 2
            command = f"{sas_address}73{data_length:02X}{command_data}"
            command_crc = get_crc(command)
            
            print(f"[AFT REGISTRATION] Complete registration command: {command_crc}")
            
            result2 = self.communicator.sas_send_command_with_queue("AFTRegComplete", command_crc, 1)
            print(f"[AFT REGISTRATION] Complete registration result: {result2}")
            
            return result2
            
        except Exception as e:
            print(f"[AFT REGISTRATION] Error during registration: {e}")
            raise

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
        """
        print(f"[BALANCE QUERY] Starting balance query - sender: {sender}, isforinfo: {isforinfo}, text: {sendertext}")
        
        # Reset balance values before query
        self.yanit_bakiye_tutar = 0
        self.yanit_restricted_amount = 0
        self.yanit_nonrestricted_amount = 0
        
        # Set waiting flag
        self.is_waiting_for_bakiye_sorgulama = True
        
        # Get asset number from communicator
        asset_number = "0000006C"  # Default to known asset number (108 decimal)
        if hasattr(self.communicator, 'asset_number') and self.communicator.asset_number:
            asset_number = self.communicator.asset_number
        elif hasattr(self.communicator, 'asset_number_hex') and self.communicator.asset_number_hex:
            asset_number = self.communicator.asset_number_hex
        # Note: SAS address (01) is NOT the same as asset number (0000006C)
        # Don't convert SAS address to asset number - they are different values
        
        print(f"[BALANCE QUERY] Using asset number: {asset_number}")
        
        # Construct SAS 74h command (AFT status inquiry)
        # Format: Address + Command + Asset Number
        sas_address = getattr(self.communicator, 'sas_address', '01')
        command = f"{sas_address}74{asset_number}"
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

    def komut_para_yukle(self, doincreasetransactionid, transfertype, customerbalance, customerpromo, transactionid, assetnumber, registrationkey):
        """
        Constructs and sends a command to load money onto the gaming machine.
        This function handles different transfer types like regular cash-in, jackpots, and bonuses.
        It builds a SAS AFT command (72h) with the appropriate details, matching the reference logic.
        """
        self.last_para_yukle_date = datetime.datetime.now()
        
        # Debug logging for input parameters
        print(f"[MONEY LOAD] komut_para_yukle called with:")
        print(f"[MONEY LOAD]   doincreasetransactionid: {doincreasetransactionid}")
        print(f"[MONEY LOAD]   transfertype: {transfertype}")
        print(f"[MONEY LOAD]   customerbalance: {customerbalance}")
        print(f"[MONEY LOAD]   customerpromo: {customerpromo}")
        print(f"[MONEY LOAD]   transactionid: {transactionid}")
        print(f"[MONEY LOAD]   assetnumber: {assetnumber}")
        print(f"[MONEY LOAD]   registrationkey: {registrationkey}")

        # --- Transaction ID logic (keep your class logic) ---
        if doincreasetransactionid:
            actual_transaction_id = self.get_next_transaction_id()
        else:
            actual_transaction_id = transactionid

        # --- Special transfer type handling (reference logic) ---
        RealTransferType = 0
        # These should be class attributes or fetched from config as needed
        G_Machine_IsBonusCashable = getattr(self, 'G_Machine_IsBonusCashable', 0)
        G_Config_IsCashoutSoft = getattr(self, 'G_Config_IsCashoutSoft', 0)
        JackpotWonAmount = getattr(self, 'JackpotWonAmount', 0)
        Billacceptor_LastCredit = getattr(self, 'Billacceptor_LastCredit', 0)

        # Copy input values to local vars for mutation
        cbalance = customerbalance
        cpromo = customerpromo
        ttype = transfertype

        # FIXED: Only treat as jackpot if this is an actual jackpot payout (not manual credit addition)
        # For manual credit additions, transfer types 10/11 should be treated as cashable/restricted
        # Only override balance for actual jackpot payouts (when JackpotWonAmount > 0)
        if ttype in [10, 11] and JackpotWonAmount > 0:  # Actual jackpot payout
            print(f"[MONEY LOAD] Processing as jackpot payout: {JackpotWonAmount}")
            RealTransferType = ttype
            cbalance = JackpotWonAmount
            cpromo = 0
        elif ttype == 13:  # Bonus
            print(f"[MONEY LOAD] Processing as bonus transfer")
            RealTransferType = 10
            cbalance = JackpotWonAmount
            cpromo = 0
            if G_Machine_IsBonusCashable == 0:
                RealTransferType = 0
        elif ttype == 1:  # Bill Acceptor
            print(f"[MONEY LOAD] Processing as bill acceptor transfer: {Billacceptor_LastCredit}")
            cbalance = Billacceptor_LastCredit
            cpromo = 0
            ttype = 0
        else:
            # Manual credit addition - use provided amounts
            print(f"[MONEY LOAD] Processing as manual credit addition")
            print(f"[MONEY LOAD]   Transfer type: {ttype} (10=cashable, 11=restricted, 0=non-restricted)")
            RealTransferType = ttype  # Set the real transfer type for manual additions

        cbalance_int = int(cbalance * 100)
        cpromo_int = int(cpromo * 100)
        
        print(f"[MONEY LOAD] Final amounts: cbalance={cbalance}, cpromo={cpromo}")
        print(f"[MONEY LOAD] Final amounts (cents): cbalance_int={cbalance_int}, cpromo_int={cpromo_int}")

        # Early exit if nothing to load
        if cbalance == 0 and cpromo == 0:
            self.is_waiting_for_para_yukle = 0
            # Optionally: self.CashIn_CompletedBy = "No-Money"
            print("[MONEY LOAD] No money to load - both cbalance and cpromo are 0.")
            return None

        # --- Command construction (reference logic) ---
        # FIXED: Command should start with SAS address, not asset number
        sas_address = getattr(self.communicator, 'sas_address', '01')
        command_header = sas_address + "72"
        command = "0000"  # Transfer Code, Transfer Index

        if RealTransferType in [10, 11]:
            command += f"{RealTransferType:02d}"  # FIXED: Use decimal format, not hex
        else:
            command += "00"

        if ttype == 13:
            if G_Machine_IsBonusCashable == 1:
                command += add_left_bcd(str(cbalance_int), 5)
                command += add_left_bcd("0", 5)
                command += add_left_bcd("0", 5)
            else:  # Promo-based bonus
                command += add_left_bcd("0", 5)
                command += add_left_bcd(str(cbalance_int), 5)
                command += add_left_bcd("0", 5)
        else:
            command += add_left_bcd(str(cbalance_int), 5)
            command += add_left_bcd(str(cpromo_int), 5)
            command += "0000000000"

        # Transfer flag
        command += "03" if G_Config_IsCashoutSoft == 1 else "07"
        command += assetnumber
        command += registrationkey

        # Transaction ID as hex string
        transaction_id_hex = ''.join(f"{ord(c):02x}" for c in str(actual_transaction_id))
        command += add_left_bcd(str(len(transaction_id_hex) // 2), 1)
        command += transaction_id_hex
        command += "00000000"  # Expiration Date
        # Pool ID
        command += "0030" if ttype == 13 or cpromo > 0 else "0000"
        command += "00"  # Receipt data length

        command_header += hex(len(command) // 2).replace("0x", "")
        full_command = get_crc(command_header + command)
        
        # Debug logging for the constructed command
        print(f"[MONEY LOAD] AFT Command constructed:")
        print(f"[MONEY LOAD]   RealTransferType: {RealTransferType}")
        print(f"[MONEY LOAD]   Command header: {command_header}")
        print(f"[MONEY LOAD]   Command data: {command}")
        print(f"[MONEY LOAD]   Full command: {full_command}")
        
        self.communicator.sas_send_command_with_queue("ParaYukle", full_command, 1)

        return actual_transaction_id

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
            print(f"[BALANCE RESPONSE] Received balance response: {yanit}")
            print(f"[BALANCE RESPONSE] Response length: {len(yanit)} characters")
            
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
                cashable_amount = int(current_cashable_amount, 16) / 100
                print(f"[BALANCE RESPONSE] Cashable Amount: {cashable_amount}")
            except ValueError:
                print(f"[BALANCE RESPONSE] Error converting cashable amount: {current_cashable_amount}")
                cashable_amount = 0
            
            # Current restricted amount (5 bytes BCD)
            current_restricted_amount = yanit[index:index+10] if index + 10 <= len(yanit) else "0000000000"
            index += 10
            print(f"[BALANCE RESPONSE] Current Restricted Amount (raw): {current_restricted_amount}")
            
            if not self.is_valid_bcd(current_restricted_amount):
                current_restricted_amount = "0000000000"
            
            try:
                restricted_amount = int(current_restricted_amount, 16) / 100
                print(f"[BALANCE RESPONSE] Restricted Amount: {restricted_amount}")
            except ValueError:
                restricted_amount = 0
            
            # Current non-restricted amount (5 bytes BCD)
            current_nonrestricted_amount = yanit[index:index+10] if index + 10 <= len(yanit) else "0000000000"
            index += 10
            print(f"[BALANCE RESPONSE] Current Non-restricted Amount (raw): {current_nonrestricted_amount}")
            
            if not self.is_valid_bcd(current_nonrestricted_amount):
                current_nonrestricted_amount = "0000000000"
            
            try:
                nonrestricted_amount = int(current_nonrestricted_amount, 16) / 100
                print(f"[BALANCE RESPONSE] Non-restricted Amount: {nonrestricted_amount}")
            except ValueError:
                nonrestricted_amount = 0
            
            # Update balance fields
            self.yanit_bakiye_tutar = cashable_amount
            self.yanit_restricted_amount = restricted_amount
            self.yanit_nonrestricted_amount = nonrestricted_amount
            
            # Clear waiting flag - this will signal the async wait function
            self.is_waiting_for_bakiye_sorgulama = False
            
            print(f"[BALANCE RESPONSE] Balance parsed successfully:")
            print(f"[BALANCE RESPONSE]   Cashable: {cashable_amount}")
            print(f"[BALANCE RESPONSE]   Restricted: {restricted_amount}")
            print(f"[BALANCE RESPONSE]   Non-restricted: {nonrestricted_amount}")
            print(f"[BALANCE RESPONSE]   Game Lock Status: {game_lock_status}")
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
        This method parses the SAS 72h response and updates transfer status.
        """
        try:
            print(f"[MONEY LOAD RESPONSE] Received response: {yanit[:20]}...")
            
            if not self.is_waiting_for_para_yukle:
                print("[MONEY LOAD RESPONSE] Not waiting for money load response, ignoring")
                return
                
            # Parse response according to SAS protocol
            # Format: Address(1) + Command(1) + Length(1) + TransactionBuffer(1) + TransferStatus(1) + ...
            index = 0
            
            # Skip address and command
            index += 4  # Address(2) + Command(2)
            
            # Get length
            length = yanit[index:index+2]
            index += 2
            
            # Get transaction buffer
            transaction_buffer = yanit[index:index+2]
            index += 2
            
            # Get transfer status (most important field)
            transfer_status = yanit[index:index+2]
            index += 2
            
            print(f"[MONEY LOAD RESPONSE] Transfer Status: {transfer_status}")
            
            # Update global transfer status
            self.global_para_yukleme_transfer_status = transfer_status
            
            # Parse amounts for logging
            amounts_info = ""
            try:
                if len(yanit) > 14:
                    cashable_amount = yanit[14:24]  # 10 chars for BCD amount
                    promo_amount = yanit[24:34] if len(yanit) > 24 else "0000000000"
                    amounts_info = f" (C:{cashable_amount} P:{promo_amount})"
            except Exception as e:
                print(f"[MONEY LOAD RESPONSE] Error parsing amounts: {e}")
            
            # Handle different transfer statuses
            if transfer_status == "00":
                print(f"[MONEY LOAD RESPONSE] Transfer successful{amounts_info}")
                self.is_waiting_for_para_yukle = 0
                
                # Parse transaction ID for validation if needed
                try:
                    if len(yanit) > 50:  # Ensure we have enough data
                        # Transaction ID is at the end, preceded by its length
                        # This is a simplified parsing - adjust based on actual response format
                        pass
                except Exception as e:
                    print(f"[MONEY LOAD RESPONSE] Error parsing transaction ID: {e}")
                    
            elif transfer_status in ["87", "84", "FF", "93", "82", "83", "81", "40"]:
                print(f"[MONEY LOAD RESPONSE] Transfer failed with status: {transfer_status}")
                if transfer_status == "87":
                    print("[MONEY LOAD RESPONSE] Machine door open, tilt, or disabled")
                elif transfer_status == "84":
                    print("[MONEY LOAD RESPONSE] Transfer amount exceeds machine limit")
                elif transfer_status == "81":
                    print("[MONEY LOAD RESPONSE] Transaction ID not unique")
                elif transfer_status == "40":
                    print("[MONEY LOAD RESPONSE] Transfer pending - continuing to wait")
                    return  # Don't clear waiting flag for pending status
                    
                # For error statuses, clear the waiting flag
                if transfer_status != "40":
                    self.is_waiting_for_para_yukle = 0
            else:
                print(f"[MONEY LOAD RESPONSE] Unknown transfer status: {transfer_status}")
                
        except Exception as e:
            print(f"[MONEY LOAD RESPONSE] Error parsing response: {e}")
            # On parse error, clear waiting flag to prevent infinite wait
            self.is_waiting_for_para_yukle = 0 

    def yanit_para_sifirla(self, yanit):
        """
        Handle AFT cashout response from the machine.
        This method parses the SAS 72h cashout response and updates cashout status.
        """
        try:
            print(f"[CASHOUT RESPONSE] Received response: {yanit[:20]}...")
            
            if not self.is_waiting_for_para_sifirla:
                print("[CASHOUT RESPONSE] Not waiting for cashout response, ignoring")
                return
                
            # Parse response according to SAS protocol
            # Format: Address(1) + Command(1) + Length(1) + TransactionBuffer(1) + TransferStatus(1) + ...
            index = 0
            
            # Skip address and command
            index += 4  # Address(2) + Command(2)
            
            # Get length
            length = yanit[index:index+2]
            index += 2
            
            # Get transaction buffer
            transaction_buffer = yanit[index:index+2]
            index += 2
            
            # Get transfer status (most important field)
            transfer_status = yanit[index:index+2]
            index += 2
            
            print(f"[CASHOUT RESPONSE] Transfer Status: {transfer_status}")
            
            # Update global transfer status
            self.global_para_silme_transfer_status = transfer_status
            
            # Parse amounts for logging
            amounts_info = ""
            try:
                if len(yanit) > 14:
                    cashout_amount = yanit[14:24]  # 10 chars for BCD amount
                    amounts_info = f" (Amount:{cashout_amount})"
            except Exception as e:
                print(f"[CASHOUT RESPONSE] Error parsing amounts: {e}")
            
            # Handle different transfer statuses
            if transfer_status == "00":
                print(f"[CASHOUT RESPONSE] Cashout successful{amounts_info}")
                self.is_waiting_for_para_sifirla = 0
                
            elif transfer_status in ["87", "84", "FF", "93", "82", "83", "81", "40"]:
                print(f"[CASHOUT RESPONSE] Cashout failed with status: {transfer_status}")
                if transfer_status == "87":
                    print("[CASHOUT RESPONSE] Machine door open, tilt, or disabled")
                elif transfer_status == "84":
                    print("[CASHOUT RESPONSE] Cashout amount exceeds machine limit")
                elif transfer_status == "83":
                    print("[CASHOUT RESPONSE] No won amount available for cashout")
                elif transfer_status == "81":
                    print("[CASHOUT RESPONSE] Transaction ID not unique")
                elif transfer_status == "40":
                    print("[CASHOUT RESPONSE] Cashout pending - continuing to wait")
                    return  # Don't clear waiting flag for pending status
                    
                # For error statuses, clear the waiting flag
                if transfer_status != "40":
                    self.is_waiting_for_para_sifirla = 0
            else:
                print(f"[CASHOUT RESPONSE] Unknown transfer status: {transfer_status}")
                
        except Exception as e:
            print(f"[CASHOUT RESPONSE] Error parsing response: {e}")
            # On parse error, clear waiting flag to prevent infinite wait
            self.is_waiting_for_para_sifirla = 0 

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