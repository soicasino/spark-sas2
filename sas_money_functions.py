# SAS Money-Related Functions Implementation
# Reference: docs/para_commands.py, docs/sas-protocol-info.md, and sample SAS code
# Implements: AFT (Advanced Funds Transfer), balance query, cashout, transfer, and related money operations

import datetime
import time
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
        # ... add other state as needed

    def komut_cancel_aft_transfer(self):
        command = "017201800BB4"
        self.communicator.sas_send_command_with_queue("CancelAFT", command, 1)

    def komut_bakiye_sorgulama(self, sender, isforinfo, sendertext='UndefinedBakiyeSorgulama'):
        command = "017400000000"
        command = get_crc(command)
        self.communicator.sas_send_command_with_queue("MoneyQuery", command, 0)
        return command

    def komut_para_yukle(self, doincreasetransactionid, transfertype, customerbalance, customerpromo, transactionid, assetnumber, registrationkey):
        self.last_para_yukle_date = datetime.datetime.now()
        if doincreasetransactionid:
            transactionid += 1
        command_header = assetnumber + "72"
        command = "00"  # transfer code
        command += "00"  # transfer index
        if transfertype == 10:
            command += "10"
        elif transfertype == 11:
            command += "11"
        else:
            command += "00"
        customerbalanceint = int(customerbalance * 100)
        command += add_left_bcd(str(customerbalanceint), 5)
        command += add_left_bcd(str(int(customerpromo * 100)), 5)
        command += "0000000000"  # nonrestricted amount
        command += "07"  # transfer flag (hard mode)
        command += assetnumber
        command += registrationkey
        transaction_id_hex = ''.join(f"{ord(c):02x}" for c in str(transactionid))
        command += add_left_bcd(str(len(transaction_id_hex) // 2), 1)
        command += transaction_id_hex
        command += "00000000"  # expiration date
        command += "0000"  # pool id
        command += "00"  # receipt data length
        command_header += hex(len(command) // 2).replace("0x", "")
        full_command = get_crc(command_header + command)
        self.communicator.sas_send_command_with_queue("ParaYukle", full_command, 1)

    def komut_para_sifirla(self, doincreaseid, transactionid, assetnumber, registrationkey):
        self.last_para_sifirla_date = datetime.datetime.now()
        if doincreaseid:
            transactionid += 1
        command_header = assetnumber + "72"
        command = "00"  # transfer code
        command += "00"  # transfer index
        command += "80"  # transfer type
        command += add_left_bcd(str(int(self.yanit_bakiye_tutar * 100)), 5)
        command += add_left_bcd(str(int(self.yanit_restricted_amount * 100)), 5)
        command += add_left_bcd(str(int(self.yanit_nonrestricted_amount * 100)), 5)
        command += "0F"  # transfer flag (hard mode)
        command += assetnumber
        command += registrationkey
        transaction_id_hex = ''.join(f"{ord(c):02x}" for c in str(transactionid))
        command += add_left_bcd(str(len(transaction_id_hex) // 2), 1)
        command += transaction_id_hex
        command += "00000000"  # expiration date
        command += self.yanit_restricted_pool_id if len(self.yanit_restricted_pool_id) == 4 else "0030"
        command += "00"  # receipt data length
        command_header += hex(len(command) // 2).replace("0x", "")
        full_command = get_crc(command_header + command)
        self.communicator.sas_send_command_with_queue("Cashout", full_command, 1)

    def yanit_bakiye_sorgulama(self, yanit):
        # Parse balance query response (simplified)
        index = 0
        address = yanit[index:index+2]
        index += 2
        command = yanit[index:index+2]
        index += 2
        length = yanit[index:index+2]
        index += 2
        asset_number = yanit[index:index+8]
        index += 8
        game_lock_status = yanit[index:index+2]
        index += 2
        available_transfers = yanit[index:index+2]
        index += 2
        host_cashout_status = yanit[index:index+2]
        index += 2
        aft_status = yanit[index:index+2]
        index += 2
        max_buffer_index = yanit[index:index+2]
        index += 2
        current_cashable_amount = yanit[index:index+10]
        index += 10
        current_restricted_amount = yanit[index:index+10]
        index += 10
        current_nonrestricted_amount = yanit[index:index+10]
        index += 10
        # ... parse more as needed
        self.yanit_bakiye_tutar = Decimal(current_cashable_amount) / 100
        self.yanit_restricted_amount = Decimal(current_restricted_amount) / 100
        self.yanit_nonrestricted_amount = Decimal(current_nonrestricted_amount) / 100
        print(f"Balance received: cashable={self.yanit_bakiye_tutar}, restricted={self.yanit_restricted_amount}, nonrestricted={self.yanit_nonrestricted_amount}")

    def komut_get_meter(self, isall=0, gameid=0):
        print("=== METER: komut_get_meter called ===")
        print(f"METER: komut_get_meter params: isall={isall}, gameid={gameid}")
        # Removed buffer clear to avoid missing fast meter responses
        G_CasinoId = int(self.config.get('casino', 'casinoid') or 8)
        IsNewMeter = 1 if G_CasinoId in [8, 11, 7] else 0
        if isall == 0 and IsNewMeter == 0:
            command = get_crc("012F0C0000A0B802031E00010BA2BA")
        elif isall == 0 and IsNewMeter == 1:
            command = get_crc("01AF1E000000A000B800020003001E00000001000B00A200BA00050006000C00")
        elif isall == 1:
            command = get_crc("012F0C00000405060C191D7FFAFBFC")
        elif isall == 2:
            command = get_crc("01AF1E000000A000B800020003001E00000001000B00A200BA00050006000C00")
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