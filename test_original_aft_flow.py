#!/usr/bin/env python3
"""
Complete Original AFT Flow Test Application - CORRECTED VERSION

This application replicates the exact AFT implementation from the original working code
with all necessary functions incorporated from both current app and original reference.

Usage: python test_original_aft_flow.py <amount>
Example: python test_original_aft_flow.py 5.00
"""

import sys
import time
import datetime
import configparser
from decimal import Decimal
import serial
import threading

class OriginalAFTFlowTest:
    """
    Complete AFT implementation with all original functions - CORRECTED
    """
    
    def __init__(self, config_file="config.ini"):
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Original global variables (exact replicas)
        self.Global_ParaYukleme_TransferStatus = "0"
        self.IsWaitingForParaYukle = 0
        self.CashIn_CompletedBy = ""
        self.G_SAS_LastAFTOperation = ""
        self.Yukle_FirstTransaction = 0
        self.Yukle_LastTransaction = 0
        self.Last_ParaYukle_TransferType = 0
        self.Global_Count_YanitHandle = 0
        self.Last_ParaYukleDate = datetime.datetime.now()
        
        # Balance variables
        self.Yanit_BakiyeTutar = Decimal(0)
        self.Yanit_RestrictedAmount = Decimal(0)
        self.Yanit_NonRestrictedAmount = Decimal(0)
        self.IsWaitingForBakiyeSorgulama = 0
        
        # AFT Registration status
        self.IsRegistrationReady = False
        
        # Serial communication
        self.serial_port = None
        self.is_connected = False
        
        # Get configuration values from config.ini
        self.asset_number = int(self.config.get('SAS_MACHINE', 'asset_number', fallback='108'))
        self.registration_key = self.config.get('SAS_MACHINE', 'registration_key', fallback='0000000000000000000000000000000000000000')
        self.sas_address = self.config.get('SAS_MACHINE', 'sas_address', fallback='01')
        
        # Convert asset number to little-endian hex format
        self.asset_number_hex = f"{self.asset_number:08X}"
        # Convert to little-endian (swap bytes)
        self.asset_number_le = ""
        for i in range(3, -1, -1):
            self.asset_number_le += self.asset_number_hex[i*2:(i*2)+2]
        
        print(f"🔧 Original AFT Flow Test Initialized - CORRECTED VERSION")
        print(f"   Asset Number: {self.asset_number} (decimal)")
        print(f"   Asset Number (hex): {self.asset_number_hex}")
        print(f"   Asset Number (little-endian): {self.asset_number_le}")
        print(f"   Registration Key: {self.registration_key}")
        print(f"   SAS Address: {self.sas_address}")
        print(f"   Port: /dev/ttyUSB1")
    
    def connect_serial(self):
        """Connect to SAS serial port /dev/ttyUSB1"""
        try:
            port_name = "/dev/ttyUSB1"
            
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=19200,
                timeout=0.1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.is_connected = True
            print(f"✅ Connected to SAS port: {port_name}")
            
            # Start background reader thread
            reader_thread = threading.Thread(target=self._serial_reader, daemon=True)
            reader_thread.start()
            
            # Test connectivity with a simple ping
            print(f"🔍 [CONNECT] Testing machine connectivity...")
            self._test_machine_connectivity()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to SAS port: {e}")
            return False
    
    def _test_machine_connectivity(self):
        """Send multiple test commands to check machine connectivity"""
        try:
            print(f"🔍 [CONNECT] === CONNECTIVITY DIAGNOSTICS ===")
            
            if not self.serial_port:
                print(f"❌ [CONNECT] No serial port available")
                return
            
            # Test 1: General poll for address 01
            general_poll = "0180F037"  # General poll for address 01
            print(f"🔍 [CONNECT] Test 1: General poll (addr 01): {general_poll}")
            command_bytes = bytes.fromhex(general_poll)
            self.serial_port.write(command_bytes)
            self.serial_port.flush()
            time.sleep(0.3)
            
            # Test 2: Try address 00 (broadcast)
            general_poll_00 = "0080B037"  # General poll for address 00
            print(f"🔍 [CONNECT] Test 2: General poll (addr 00): {general_poll_00}")
            command_bytes = bytes.fromhex(general_poll_00)
            self.serial_port.write(command_bytes)
            self.serial_port.flush()
            time.sleep(0.3)
            
            # Test 3: Simple enable command
            enable_cmd = "018022C3"  # Enable gaming machine command
            print(f"🔍 [CONNECT] Test 3: Enable command: {enable_cmd}")
            command_bytes = bytes.fromhex(enable_cmd)
            self.serial_port.write(command_bytes)
            self.serial_port.flush()
            time.sleep(0.3)
            
            # Test 4: Exception Reset (clear error state)
            exception_reset = "017E00E837"  # Exception reset command
            print(f"🔍 [CONNECT] Test 4: Exception reset: {exception_reset}")
            command_bytes = bytes.fromhex(exception_reset)
            self.serial_port.write(command_bytes)
            self.serial_port.flush()
            time.sleep(0.3)
            
            print(f"🔍 [CONNECT] All test commands sent.")
            print(f"🔍 [CONNECT] === MACHINE STATE DIAGNOSIS ===")
            print(f"🔍 [CONNECT] If seeing continuous 01 bytes:")
            print(f"🔍 [CONNECT] - Machine is responding but in error state")
            print(f"🔍 [CONNECT] - Try machine reset or clear error conditions")
            print(f"🔍 [CONNECT] - Check machine display for tilt/error messages")
            print(f"🔍 [CONNECT] - Machine may need door opened/closed cycle")
            print(f"🔍 [CONNECT] ")
            print(f"🔍 [CONNECT] If no data received:")
            print(f"🔍 [CONNECT] - Not powered on")
            print(f"🔍 [CONNECT] - Not in SAS mode") 
            print(f"🔍 [CONNECT] - Using different SAS address")
            print(f"🔍 [CONNECT] - Using different baud rate")
            print(f"🔍 [CONNECT] - Serial cable disconnected")
            
        except Exception as e:
            print(f"❌ [CONNECT] Error in connectivity test: {e}")
    
    def _serial_reader(self):
        """Background thread to read SAS responses with enhanced debugging"""
        buffer = ""
        
        while self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    hex_data = data.hex().upper()
                    buffer += hex_data
                    
                    print(f"🔍 [SERIAL] <<<< RECEIVED DATA: {hex_data}")
                    
                    # Handle special case: continuous 01 bytes (machine error/polling state)
                    if hex_data == "01":
                        # Count consecutive 01 bytes
                        if not hasattr(self, '_consecutive_01_count'):
                            self._consecutive_01_count = 0
                        self._consecutive_01_count += 1
                        
                        if self._consecutive_01_count == 1:
                            print(f"⚠️  [SERIAL] Machine sending 01 bytes - possible error state or polling")
                        elif self._consecutive_01_count == 10:
                            print(f"⚠️  [SERIAL] Machine in continuous 01 state - this indicates:")
                            print(f"⚠️  [SERIAL] - Machine may be in error/tilt state")  
                            print(f"⚠️  [SERIAL] - SAS address conflict (machine expects different address)")
                            print(f"⚠️  [SERIAL] - Machine not ready for SAS communication")
                            print(f"⚠️  [SERIAL] - Need to clear machine state or reset")
                        elif self._consecutive_01_count % 50 == 0:
                            print(f"⚠️  [SERIAL] Still receiving 01 bytes ({self._consecutive_01_count} total)")
                        
                        # Don't process 01 bytes as normal messages
                        buffer = ""  # Clear buffer
                        continue
                    else:
                        # Reset 01 counter when we get other data
                        if hasattr(self, '_consecutive_01_count'):
                            if self._consecutive_01_count > 0:
                                print(f"🔍 [SERIAL] Normal data received after {self._consecutive_01_count} x 01 bytes")
                            self._consecutive_01_count = 0
                    
                    # Process complete messages (skip if buffer only contains 01s)
                    while len(buffer) >= 6 and buffer != "01" * (len(buffer) // 2):  # Minimum message length
                        # Find message start (address)
                        if buffer.startswith(self.sas_address.upper()):
                            try:
                                # Get command and length
                                if len(buffer) >= 6:
                                    command = buffer[2:4]
                                    length_hex = buffer[4:6]
                                    length = int(length_hex, 16)
                                    total_length = 6 + (length * 2)  # Header + data + CRC
                                    
                                    print(f"🔍 [SERIAL] Valid message detected - Command: {command}, Length: {length}, Total: {total_length}")
                                    
                                    if len(buffer) >= total_length:
                                        message = buffer[:total_length]
                                        buffer = buffer[total_length:]
                                        print(f"🔍 [SERIAL] Complete message extracted: {message}")
                                        self._process_sas_response(message)
                                    else:
                                        print(f"🔍 [SERIAL] Waiting for more data ({len(buffer)}/{total_length})")
                                        break  # Wait for more data
                                else:
                                    break
                            except Exception as e:
                                print(f"🔍 [SERIAL] Error parsing message header: {e}")
                                # Remove invalid start and continue
                                buffer = buffer[2:]
                        else:
                            # Remove invalid character
                            if len(buffer) >= 2:
                                invalid_char = buffer[:2]
                                if invalid_char != "01":  # Don't spam about 01 bytes
                                    print(f"🔍 [SERIAL] Invalid start byte, removing: {invalid_char}")
                                buffer = buffer[2:]
                            else:
                                buffer = ""
                else:
                    # Periodically log that we're listening
                    if hasattr(self, '_debug_counter'):
                        self._debug_counter += 1
                    else:
                        self._debug_counter = 0
                    
                    if self._debug_counter % 5000 == 0:  # Every ~5 seconds  
                        print(f"🔍 [SERIAL] Listening for SAS responses... (no data received)")
                
                time.sleep(0.001)  # 1ms delay
                
            except Exception as e:
                print(f"❌ [SERIAL] Error in serial reader: {e}")
                time.sleep(0.1)
    
    def _process_sas_response(self, response):
        """Process SAS response messages with enhanced debugging"""
        try:
            print(f"📥 [SAS] RAW Response: {response}")
            
            if len(response) >= 4:
                command = response[2:4]
                print(f"📥 [SAS] Command Code: {command}")
                
                if command == "5A":  # AFT registration response
                    print(f"📥 [SAS] AFT Registration Response detected")
                    self._handle_aft_registration_response(response)
                elif command == "72":  # AFT transfer response
                    print(f"📥 [SAS] AFT Transfer Response detected")
                    self.Yanit_ParaYukle(response)
                elif command == "74":  # Balance response
                    print(f"📥 [SAS] Balance Response detected")
                    self.Yanit_BakiyeSorgulama(response)
                elif response == "01FF69DB5B":  # AFT completion exception
                    print(f"📥 [SAS] AFT completion exception detected")
                    if self.IsWaitingForParaYukle == 1:
                        self.Global_ParaYukleme_TransferStatus = "00"  # Mark as completed
                        print(f"📥 [SAS] AFT marked as completed via exception")
                else:
                    print(f"📥 [SAS] Other response - Command: {command}")
                    
        except Exception as e:
            print(f"❌ [SAS] Error processing response: {e}")
    
    def _handle_aft_registration_response(self, response):
        """Handle AFT registration response"""
        try:
            print(f"📥 [REG] Processing AFT registration response: {response}")
            
            if len(response) >= 8:
                # Registration status is typically in position 6-7
                reg_status = response[6:8]
                print(f"📥 [REG] Registration Status: {reg_status}")
                
                if reg_status == "00":
                    self.IsRegistrationReady = True
                    print(f"✅ [REG] AFT Registration SUCCESSFUL - Ready for transfers")
                else:
                    print(f"❌ [REG] AFT Registration FAILED - Status: {reg_status}")
                    self.IsRegistrationReady = False
            else:
                print(f"❌ [REG] Registration response too short: {len(response)}")
                
        except Exception as e:
            print(f"❌ [REG] Error processing registration response: {e}")
    
    def send_sas_command(self, command_name, command_hex):
        """Send SAS command to machine"""
        try:
            if not self.is_connected or not self.serial_port:
                print(f"❌ Not connected to SAS port")
                return False
            
            # Convert hex string to bytes
            command_bytes = bytes.fromhex(command_hex)
            
            print(f"📤 Sending {command_name}: {command_hex}")
            self.serial_port.write(command_bytes)
            self.serial_port.flush()
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending SAS command: {e}")
            return False
    
    def get_crc(self, command_hex):
        """Calculate CRC for SAS command (exact replica of original)"""
        try:
            # Remove any existing CRC
            if len(command_hex) >= 4:
                command_hex = command_hex[:-4]
            
            # Convert to bytes
            data = bytes.fromhex(command_hex)
            
            # Calculate CRC16 (SAS standard)
            crc = 0
            for byte in data:
                crc ^= byte
                for _ in range(8):
                    if crc & 1:
                        crc = (crc >> 1) ^ 0x8408
                    else:
                        crc >>= 1
            
            # Convert to hex and append (little-endian format)
            crc_hex = f"{crc & 0xFF:02X}{(crc >> 8) & 0xFF:02X}"
            return command_hex + crc_hex
            
        except Exception as e:
            print(f"Error calculating CRC: {e}")
            return command_hex + "0000"
    
    def AddLeftBCD(self, number, length_in_bytes):
        """EXACT implementation of AddLeftBCD from original working code"""
        number = int(number)
        retdata = str(number)
        
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
    
    def AddLeftString(self, input_string, target_length):
        """EXACT implementation of AddLeftString from original working code"""
        input_string = str(input_string)
        
        while len(input_string) < target_length:
            input_string = "0" + input_string
            
        return input_string
    
    def Komut_RegisterAssetNo(self):
        """AFT Registration command - CORRECTED to match original working code"""
        try:
            print(f"🔧 [AFT REGISTRATION] Starting asset registration (2-step process)...")
            
            # STEP 1: Initialize registration (exact original)
            print(f"🔧 [AFT REGISTRATION] Step 1: Initialize registration")
            init_command = f"{self.sas_address}7301FF"  # Address + Command 73 + Length 01 + Data FF
            init_command_crc = self.get_crc(init_command)
            print(f"🔧 [AFT REGISTRATION] Init command: {init_command_crc}")
            
            # Send init command
            init_success = self.send_sas_command("AFT_Registration_Init", init_command_crc)
            if not init_success:
                print(f"❌ [AFT REGISTRATION] Failed to send init command")
                return False
            
            # Wait for init response
            time.sleep(2)
            
            # STEP 2: Complete registration (exact original)
            print(f"🔧 [AFT REGISTRATION] Step 2: Complete registration")
            
            # Convert POS ID to BCD format (4 bytes)
            pos_id = "POS001"
            pos_id_padded = pos_id.ljust(4, '\x00')[:4]  # Pad to 4 characters
            pos_id_bcd = ''.join('{:02x}'.format(ord(c)) for c in pos_id_padded)
            print(f"🔧 [AFT REGISTRATION] POS ID BCD: {pos_id_bcd}")
            
            # Build complete registration command (exact original format)
            registration_code = "01"  # Registration code (01 for normal registration)
            command_body = registration_code + self.asset_number_le + self.registration_key + pos_id_bcd
            command_length = hex(len(command_body) // 2).replace("0x", "").upper().zfill(2)
            
            complete_command_no_crc = f"{self.sas_address}73{command_length}{command_body}"
            complete_command = self.get_crc(complete_command_no_crc)
            
            print(f"🔧 [AFT REGISTRATION] Complete registration command: {complete_command}")
            
            # Send complete command
            complete_success = self.send_sas_command("AFT_Registration_Complete", complete_command)
            
            if complete_success:
                print(f"✅ [AFT REGISTRATION] AFT registration commands sent successfully")
                # Wait for registration to complete
                time.sleep(3)
                return True
            else:
                print(f"❌ [AFT REGISTRATION] Failed to send complete registration command")
                return False
                
        except Exception as e:
            print(f"❌ [AFT REGISTRATION] Error: {e}")
            return False
    
    def Komut_ParaYukle(self, doincreasetransactionid, transfertype, customerbalance=0.0, customerpromo=0.0):
        """EXACT implementation of Komut_ParaYukle from original working code - CORRECTED"""
        try:
            print(f"💰 [AFT TRANSFER] Starting money load command...")
            print(f"💰 [AFT TRANSFER] Amount: ${customerbalance:.2f}")
            print(f"💰 [AFT TRANSFER] Transfer Type: {transfertype}")
            
            self.Last_ParaYukleDate = datetime.datetime.now()
            
            # Get current transaction ID (use current asset number)
            transactionid = self.asset_number
            if doincreasetransactionid == 1:
                transactionid += 1
                if transactionid > 9999:
                    transactionid = self.asset_number
            
            print(f"💰 [AFT TRANSFER] Transaction ID: {transactionid}")
            
            # Determine real transfer type (exact original logic)
            RealTransferType = transfertype
            if transfertype == 13:
                RealTransferType = 11
            elif transfertype == 1:
                RealTransferType = 0
            
            print(f"💰 [AFT TRANSFER] Real Transfer Type: {RealTransferType}")
            
            # Convert amounts to cents and format as BCD
            customerbalance_cents = int(customerbalance * 100)
            customerpromo_cents = int(customerpromo * 100)
            
            print(f"💰 [AFT TRANSFER] Amount in cents: {customerbalance_cents}")
            print(f"💰 [AFT TRANSFER] Promo in cents: {customerpromo_cents}")
            
            # Build command
            Command = ""
            
            # Transfer type field (exact original logic)
            if RealTransferType == 10:
                Command += "10"   # Transfer Type 10 (jackpot)
            elif RealTransferType == 11:
                Command += "11"   # Transfer Type 11 (nonrestricted)
            else:
                Command += "00"   # Transfer Type 00 (CASHABLE - DEFAULT!)
            
            # Cashable amount (5 bytes BCD)
            Command += self.AddLeftBCD(customerbalance_cents, 5)
            
            # Restricted amount (5 bytes BCD)
            Command += self.AddLeftBCD(customerpromo_cents, 5)
            
            # Non-restricted amount (5 bytes BCD) - always 0
            Command += "0000000000"
            
            # Transfer flag
            Command += "07"  # Transfer flag (exact original)
            
            # Asset number (little-endian format)
            Command += self.asset_number_le
            
            # Registration key
            Command += self.registration_key
            
            # Transaction ID - FIXED: Use ASCII string encoding (like original working code)
            # The original working code actually uses string encoding, not pure BCD
            TRANSACTIONID = f"{transactionid:04d}"  # 4-digit string like "0109"
            tid_length = len(TRANSACTIONID)
            Command += f"{tid_length:02d}"  # Length as 2-digit decimal string
            Command += TRANSACTIONID  # Transaction ID as string (not hex encoded)
            
            # Expiration date (8 bytes) - all zeros
            Command += "0000000000000000"
            
            # Pool ID
            if transfertype == 13 or customerpromo > 0:
                Command += "0030"  # Pool ID for promo
            else:
                Command += "0000"  # No pool ID
            
            # Receipt data length
            Command += "00"
            
            print(f"💰 [AFT TRANSFER] Command data before header: {Command}")
            
            # Build command header with actual length
            actual_length = len(Command) // 2
            CommandHeader = f"{self.sas_address}72{actual_length:02X}"
            
            # Build final command
            full_command = CommandHeader + Command
            
            print(f"💰 [AFT TRANSFER] Full command before CRC: {full_command}")
            
            # Calculate and add CRC
            final_command = self.get_crc(full_command)
            
            print(f"💰 [AFT TRANSFER] Final AFT command: {final_command}")
            
            # Send command
            success = self.send_sas_command("AFT_Transfer", final_command)
            
            if success:
                print(f"✅ [AFT TRANSFER] AFT transfer command sent successfully")
                return transactionid
            else:
                print(f"❌ [AFT TRANSFER] Failed to send AFT transfer command")
                return None
                
        except Exception as e:
            print(f"❌ [AFT TRANSFER] Error: {e}")
            return None
    
    def Wait_ParaYukle(self, transfertype, customerbalance, timeout_seconds=30):
        """EXACT implementation of Wait_ParaYukle from original working code"""
        print(f"⏳ [AFT WAIT] Starting blocking wait for AFT completion...")
        print(f"⏳ [AFT WAIT] Timeout: {timeout_seconds} seconds")
        
        # Set waiting flag (exact original)
        self.IsWaitingForParaYukle = 1
        self.G_SAS_LastAFTOperation = "Yukle"
        self.Global_ParaYukleme_TransferStatus = "0"
        self.Yukle_FirstTransaction = 0
        self.Yukle_LastTransaction = 0
        self.Last_ParaYukle_TransferType = transfertype
        self.Global_Count_YanitHandle = 0
        
        WaitParaYukle_Date = datetime.datetime.now()
        start_time = time.time()
        
        # Send the AFT transfer command
        transaction_id = self.Komut_ParaYukle(1, transfertype, customerbalance, 0.0)
        
        if transaction_id is None:
            print(f"❌ [AFT WAIT] Failed to send AFT command")
            self.IsWaitingForParaYukle = 0
            return False
        
        print(f"⏳ [AFT WAIT] Command sent, transaction ID: {transaction_id}")
        print(f"⏳ [AFT WAIT] Entering blocking wait loop...")
        
        # Blocking while loop - exactly as original
        last_log_time = 0
        while self.IsWaitingForParaYukle == 1:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                print(f"❌ [AFT WAIT] Timeout after {timeout_seconds} seconds")
                print(f"❌ [AFT WAIT] No response from machine - check connection and machine status")
                self.IsWaitingForParaYukle = 0
                return False
            
            # Log every 5 seconds (reduced spam)
            if elapsed - last_log_time >= 5:
                print(f"⏳ [AFT WAIT] {elapsed:.1f}s - Status: {self.Global_ParaYukleme_TransferStatus}")
                print(f"⏳ [AFT WAIT] Waiting for machine response...")
                last_log_time = elapsed
            
            # Check if we got a response
            if self.Global_ParaYukleme_TransferStatus != "0":
                print(f"✅ [AFT WAIT] Transfer completed with status: {self.Global_ParaYukleme_TransferStatus}")
                
                # Reset flags
                self.IsWaitingForParaYukle = 0
                
                # Return success/failure based on status
                if self.Global_ParaYukleme_TransferStatus == "00":
                    print(f"🎉 [AFT WAIT] AFT Transfer SUCCESS!")
                    return True
                elif self.Global_ParaYukleme_TransferStatus == "C0":
                    print(f"🟡 [AFT WAIT] AFT Transfer acknowledged, checking completion...")
                    # Continue waiting for final status
                    self.Global_ParaYukleme_TransferStatus = "0"  # Reset to continue waiting
                    self.IsWaitingForParaYukle = 1  # Continue waiting
                    continue
                else:
                    print(f"❌ [AFT WAIT] AFT Transfer FAILED with status: {self.Global_ParaYukleme_TransferStatus}")
                    return False
            
            # Small delay to prevent busy waiting (exact original timing)
            time.sleep(0.1)  # Increased to 100ms to reduce CPU usage
        
        print(f"❌ [AFT WAIT] Wait loop exited unexpectedly")
        return False
    
    def Yanit_ParaYukle(self, response):
        """EXACT implementation of Yanit_ParaYukle from original working code"""
        print(f"📥 [AFT RESPONSE] Processing AFT response: {response}")
        
        # Only process if we're waiting for this response
        if self.IsWaitingForParaYukle != 1:
            print(f"📥 [AFT RESPONSE] Not waiting for AFT response, ignoring...")
            return
        
        try:
            # Extract Transfer Status from response
            # In 72h response: Address(2) + Command(2) + Length(2) + TransferStatus(2)
            if len(response) >= 8:
                transfer_status = response[6:8]  # Status at position 6-7
                print(f"📥 [AFT RESPONSE] Transfer Status: {transfer_status}")
                
                # Update global status flag (exact original)
                self.Global_ParaYukleme_TransferStatus = transfer_status
                
                # Status codes (exact original):
                status_descriptions = {
                    "00": "Transfer successful",
                    "C0": "Transfer acknowledged/pending",
                    "40": "Transfer pending",
                    "81": "Transaction ID not unique",
                    "84": "Transfer amount exceeds limit",
                    "87": "Gaming machine unable to accept transfers",
                    "80": "Gaming machine not registered",
                    "82": "Registration key mismatch",
                    "83": "No POS ID configured",
                    "FF": "No transfer information available"
                }
                
                status_desc = status_descriptions.get(transfer_status, f"Unknown status: {transfer_status}")
                print(f"📥 [AFT RESPONSE] Status meaning: {status_desc}")
                
            else:
                print(f"📥 [AFT RESPONSE] Response too short: {len(response)} characters")
                self.Global_ParaYukleme_TransferStatus = "FF"  # Error
                
        except Exception as e:
            print(f"📥 [AFT RESPONSE] Error parsing response: {e}")
            self.Global_ParaYukleme_TransferStatus = "FF"  # Error
    
    def Komut_BakiyeSorgulama(self):
        """Send balance query command (exact replica of original)"""
        try:
            print(f"💳 [BALANCE QUERY] Sending balance query...")
            
            # Build balance query command using actual asset number
            Command = f"{self.sas_address}740F{self.asset_number_le}00000000000000000000000000000000"
            
            # Calculate and add CRC
            full_command = self.get_crc(Command)
            
            print(f"💳 [BALANCE QUERY] Balance query command: {full_command}")
            
            # Send command
            success = self.send_sas_command("Balance_Query", full_command)
            
            if success:
                print(f"✅ [BALANCE QUERY] Balance query sent successfully")
                return True
            else:
                print(f"❌ [BALANCE QUERY] Failed to send balance query")
                return False
                
        except Exception as e:
            print(f"❌ [BALANCE QUERY] Error: {e}")
            return False
    
    def Yanit_BakiyeSorgulama(self, response):
        """EXACT implementation of Yanit_BakiyeSorgulama from original working code"""
        print(f"💳 [BALANCE RESPONSE] Processing balance response: {response}")
        
        try:
            # Parse response according to original working code
            index = 0
            
            Address = response[index:index+2]
            index += 2
            
            Command = response[index:index+2]
            index += 2
            
            Length = response[index:index+2]
            index += 2
            
            AssetNumber = response[index:index+8]
            index += 8
            
            GameLockStatus = response[index:index+2]
            index += 2
            
            AvailableTransfers = response[index:index+2]
            index += 2
            
            HostCashoutStatus = response[index:index+2]
            index += 2
            
            AFTStatus = response[index:index+2]
            index += 2
            
            MaxBufferIndex = response[index:index+2]
            index += 2
            
            CurrentCashableAmount = response[index:index+10]
            index += 10
            
            print(f"💳 [BALANCE RESPONSE] Parsed fields:")
            print(f"💳   Game Lock Status: {GameLockStatus}")
            print(f"💳   Available Transfers: {AvailableTransfers}")
            print(f"💳   AFT Status: {AFTStatus}")
            print(f"💳   Current Cashable Amount (raw): {CurrentCashableAmount}")
            
            if len(CurrentCashableAmount) != 10:
                print(f"💳 [BALANCE RESPONSE] ⚠️  Incomplete cashable amount!")
                return
            
            # Convert BCD to decimal (exact original)
            try:
                # Parse BCD format properly
                amount_str = ""
                for i in range(0, len(CurrentCashableAmount), 2):
                    byte_val = CurrentCashableAmount[i:i+2]
                    amount_str += byte_val
                
                Tutar = Decimal(int(amount_str)) / 100
                self.Yanit_BakiyeTutar = Tutar
                
                print(f"💳 [BALANCE RESPONSE] Cashable Balance: ${Tutar}")
                
            except Exception as e:
                print(f"💳 [BALANCE RESPONSE] Error converting amount: {e}")
                self.Yanit_BakiyeTutar = Decimal(0)
            
            # Handle restricted and non-restricted amounts if present
            if index + 10 <= len(response):
                CurrentRestrictedAmount = response[index:index+10]
                index += 10
                
                try:
                    amount_str = ""
                    for i in range(0, len(CurrentRestrictedAmount), 2):
                        byte_val = CurrentRestrictedAmount[i:i+2]
                        amount_str += byte_val
                    
                    Y_RestrictedAmount = Decimal(int(amount_str)) / 100
                    self.Yanit_RestrictedAmount = Y_RestrictedAmount
                    print(f"💳 [BALANCE RESPONSE] Restricted Balance: ${Y_RestrictedAmount}")
                except:
                    self.Yanit_RestrictedAmount = Decimal(0)
            
            if index + 10 <= len(response):
                CurrentNonrestrictedAmount = response[index:index+10]
                index += 10
                
                try:
                    amount_str = ""
                    for i in range(0, len(CurrentNonrestrictedAmount), 2):
                        byte_val = CurrentNonrestrictedAmount[i:i+2]
                        amount_str += byte_val
                    
                    Y_NonRestrictedAmount = Decimal(int(amount_str)) / 100
                    self.Yanit_NonRestrictedAmount = Y_NonRestrictedAmount
                    print(f"💳 [BALANCE RESPONSE] Non-restricted Balance: ${Y_NonRestrictedAmount}")
                except:
                    self.Yanit_NonRestrictedAmount = Decimal(0)
            
            # Clear waiting flag
            self.IsWaitingForBakiyeSorgulama = 0
            
            print(f"💳 [BALANCE RESPONSE] ✅ Balance parsed successfully")
            print(f"💳 [BALANCE RESPONSE] Total: ${self.Yanit_BakiyeTutar + self.Yanit_RestrictedAmount + self.Yanit_NonRestrictedAmount}")
            
        except Exception as e:
            print(f"💳 [BALANCE RESPONSE] Error parsing balance response: {e}")
            self.IsWaitingForBakiyeSorgulama = 0
    
    def Wait_BakiyeSorgulama(self, timeout_seconds=10):
        """Wait for balance query response (exact replica of original)"""
        print(f"💳 [BALANCE WAIT] Starting balance query wait...")
        
        # Set waiting flag
        self.IsWaitingForBakiyeSorgulama = 1
        
        # Send balance query
        query_sent = self.Komut_BakiyeSorgulama()
        
        if not query_sent:
            self.IsWaitingForBakiyeSorgulama = 0
            return False
        
        start_time = time.time()
        
        # Wait for response
        while self.IsWaitingForBakiyeSorgulama == 1:
            if time.time() - start_time > timeout_seconds:
                print(f"💳 [BALANCE WAIT] ⏰ Timeout after {timeout_seconds} seconds")
                self.IsWaitingForBakiyeSorgulama = 0
                return False
            
            time.sleep(0.1)  # Check every 100ms
        
        print(f"💳 [BALANCE WAIT] ✅ Balance response received")
        return True
    
    def run_complete_aft_test(self, amount):
        """Run the complete AFT test with exact original flow - CORRECTED"""
        
        print(f"\n============================================================")
        print(f"🧪 ORIGINAL AFT FLOW TEST - EXACT REPLICA (CORRECTED)")
        print(f"============================================================")
        print(f"💰 Test Amount: ${amount:.2f}")
        
        # Step 1: Connect to SAS
        print(f"\n--- STEP 1: Connect to SAS ---")
        if not self.connect_serial():
            return False
        
        # Give time for connection to stabilize and see connectivity test
        print(f"⏱️  Waiting 2 seconds for connection to stabilize...")
        time.sleep(2)
        
        # Step 2: Clear machine errors and enable
        print(f"\n--- STEP 2: Clear Machine Errors and Enable ---")
        print(f"🔧 [MACHINE] Attempting to clear machine error state...")
        
        # Try to clear machine state with enable commands
        enable_commands = [
            ("Exception Reset", f"{self.sas_address}7E00"),
            ("Enable Gaming Machine", f"{self.sas_address}8001"), 
            ("AFT Clear Registration", f"{self.sas_address}7300"),
        ]
        
        for name, cmd_base in enable_commands:
            try:
                cmd_with_crc = self.get_crc(cmd_base)
                print(f"🔧 [MACHINE] Sending {name}: {cmd_with_crc}")
                self.send_sas_command(name, cmd_with_crc)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  [MACHINE] {name} failed: {e}")
        
        print(f"⏱️  [MACHINE] Waiting 3 seconds for machine to stabilize...")
        time.sleep(3)
        
        # Step 3: AFT Registration with response check
        print(f"\n--- STEP 3: AFT Registration ---")
        print(f"🔧 [AFT REGISTRATION] Starting asset registration...")
        
        registration_success = self.Komut_RegisterAssetNo()
        if not registration_success:
            print(f"❌ [AFT REGISTRATION] Registration command failed")
            return False
        
        # Wait for registration response
        print(f"🔧 [AFT REGISTRATION] Waiting for registration response...")
        for i in range(50):  # 5 second timeout
            if self.IsRegistrationReady:
                break
            time.sleep(0.1)
        
        if not self.IsRegistrationReady:
            print(f"⚠️  [AFT REGISTRATION] No registration response received, but continuing...")
        else:
            print(f"✅ [AFT REGISTRATION] Registration confirmed ready")
        
        # Add mandatory 3-second wait after registration (as per original flow)
        print(f"⏱️  [AFT REGISTRATION] Mandatory 3-second wait after registration...")
        time.sleep(3)
        
        # Step 3: Initial Balance Query (diagnostic)
        print(f"\n--- STEP 4: Initial Balance Query ---")
        print(f"💳 [BALANCE WAIT] Starting balance query wait...")
        
        balance_success = self.Wait_BakiyeSorgulama(timeout_seconds=10)
        if not balance_success:
            print(f"⚠️  Initial balance query failed, continuing...")
        else:
            print(f"✅ Initial balance: ${self.Yanit_BakiyeTutar:.2f}")
        
        # Step 4: AFT Transfer (Original Flow)
        print(f"\n--- STEP 5: AFT Transfer (Original Flow) ---")
        
        # Use exact original Wait_ParaYukle function
        transfer_success = self.Wait_ParaYukle(0, amount, timeout_seconds=30)
        
        if transfer_success:
            print(f"\n🎉 AFT TRANSFER COMPLETED SUCCESSFULLY!")
            
            # Step 5: Post-transfer balance check
            print(f"\n--- STEP 5: Post-Transfer Balance Check ---")
            
            # Add 5-second wait (as per original flow)
            print(f"⏱️  Post-transfer 5-second wait...")
            time.sleep(5)
            
            final_balance_success = self.Wait_BakiyeSorgulama(timeout_seconds=10)
            if final_balance_success:
                print(f"💰 Final balance: ${self.Yanit_BakiyeTutar:.2f}")
                
                # Check if balance increased
                if self.Yanit_BakiyeTutar >= amount:
                    print(f"✅ BALANCE VERIFICATION: Success! Balance reflects the transfer.")
                    return True
                else:
                    print(f"⚠️  BALANCE VERIFICATION: Balance did not increase as expected.")
                    return False
            else:
                print(f"❌ Failed to get final balance")
                return False
        else:
            print(f"\n❌ AFT TRANSFER FAILED!")
            return False


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_original_aft_flow.py <amount>")
        print("Example: python test_original_aft_flow.py 5.00")
        sys.exit(1)
    
    try:
        amount = float(sys.argv[1])
        if amount <= 0:
            print("Amount must be positive")
            sys.exit(1)
    except ValueError:
        print("Invalid amount format")
        sys.exit(1)
    
    print(f"🚀 Starting Original AFT Flow Test")
    print(f"💰 Amount: ${amount:.2f}")
    print()
    
    # Create and run test
    test_app = OriginalAFTFlowTest()
    success = test_app.run_complete_aft_test(amount)
    
    print(f"\n" + "="*60)
    if success:
        print("🎉 ORIGINAL AFT FLOW TEST PASSED!")
        print("The AFT system is working correctly using original logic.")
    else:
        print("❌ ORIGINAL AFT FLOW TEST FAILED!")
        print("There may be an issue with the AFT implementation or machine setup.")
    print("="*60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 