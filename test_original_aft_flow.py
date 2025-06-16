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
        print(f"   Port: /dev/ttyUSB0")
    
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
            
            print(f"🔍 [CONNECT] All test commands sent. If no data received above, machine may be:")
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
                    
                    # Process complete messages
                    while len(buffer) >= 6:  # Minimum message length
                        # Find message start (address)
                        if buffer.startswith(self.sas_address.upper()):
                            try:
                                # Get command and length
                                if len(buffer) >= 6:
                                    command = buffer[2:4]
                                    length_hex = buffer[4:6]
                                    length = int(length_hex, 16)
                                    total_length = 6 + (length * 2)  # Header + data + CRC
                                    
                                    print(f"🔍 [SERIAL] Message detected - Command: {command}, Length: {length}, Total: {total_length}")
                                    
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
                            print(f"🔍 [SERIAL] Invalid start byte, removing: {buffer[:2] if len(buffer) >= 2 else buffer}")
                            buffer = buffer[2:] if len(buffer) >= 2 else ""
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
        """AFT Registration command - exact replica of original"""
        try:
            print(f"🔧 [AFT REGISTRATION] Starting asset registration...")
            
            # Build registration command using actual asset number
            Command = "015A17"  # Address + Command + Length
            Command += self.asset_number_le  # Asset number (little-endian format)
            Command += self.registration_key  # Registration key
            Command += "504F5330303100"  # POS ID "POS001" + null terminator
            
            # Calculate and add CRC
            full_command = self.get_crc(Command)
            
            print(f"🔧 [AFT REGISTRATION] Registration command: {full_command}")
            
            # Send command
            success = self.send_sas_command("AFT_Registration", full_command)
            
            if success:
                print(f"✅ [AFT REGISTRATION] Registration command sent successfully")
                return True
            else:
                print(f"❌ [AFT REGISTRATION] Failed to send registration command")
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
            CommandHeader = f"0172{actual_length:02X}"
            
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
            Command = f"01740F{self.asset_number_le}00000000000000000000000000000000"
            
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
        
        # Step 2: AFT Registration with response check
        print(f"\n--- STEP 2: AFT Registration ---")
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
        print(f"\n--- STEP 3: Initial Balance Query ---")
        print(f"💳 [BALANCE WAIT] Starting balance query wait...")
        
        balance_success = self.Wait_BakiyeSorgulama(timeout_seconds=10)
        if not balance_success:
            print(f"⚠️  Initial balance query failed, continuing...")
        else:
            print(f"✅ Initial balance: ${self.Yanit_BakiyeTutar:.2f}")
        
        # Step 4: AFT Transfer (Original Flow)
        print(f"\n--- STEP 4: AFT Transfer (Original Flow) ---")
        
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