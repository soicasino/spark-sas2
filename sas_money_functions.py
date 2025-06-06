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
        G_CasinoId = int(self.config.get('casino', 'casinoid', fallback=8))
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
    }

    def handle_single_meter_response(self, tdata):
        """
        Dynamically and robustly parses a meter block or single meter response.
        Fixes BCD conversion by treating the hex string as a base-10 integer.
        """
        print(f"--- Parsing Meter Response: {tdata} ---")
        # Check for a long poll response (meter block)
        if len(tdata) > 20:  # A typical single meter response is shorter
            idx = 6  # Skip address (2), command code (2), and length (2)
            parsed_meters = {}
            while idx + 4 <= len(tdata): # Need at least a 2-byte code and 2-byte value
                code = tdata[idx:idx+2].upper()
                idx += 2

                if code not in self.METER_CODE_MAP:
                    print(f"Warning: Unknown meter code '{code}'. Attempting to skip.")
                    # As a fallback, assume a 4-byte value and skip
                    idx += 8 
                    continue

                name, nbytes = self.METER_CODE_MAP[code]
                hex_len = nbytes * 2
                value_hex = tdata[idx:idx + hex_len]
                idx += hex_len

                if len(value_hex) < hex_len:
                    print(f"Error: Incomplete data for meter '{name}'. Expected {hex_len} chars, got {len(value_hex)}.")
                    continue

                if self.is_valid_bcd(value_hex):
                    # CORRECTED BCD CONVERSION
                    value = self.bcd_to_int(value_hex) / 100.0
                    parsed_meters[name] = value
                    print(f"  {name} ({code}): {value:,.2f}")
                else:
                    print(f"Error: Invalid BCD format for meter '{name}': {value_hex}")
            print("--- End of Meter Block ---")
            return parsed_meters
        # Handle a single meter response as a fallback
        elif len(tdata) >= 14: # Min length for a single response (e.g., 012F + len + code + 4-byte val + crc)
            code = tdata[6:8].upper()
            if code in self.METER_CODE_MAP:
                name, nbytes = self.METER_CODE_MAP[code]
                hex_len = nbytes * 2
                value_hex = tdata[8:8 + hex_len]

                if self.is_valid_bcd(value_hex):
                    # CORRECTED BCD CONVERSION
                    value = self.bcd_to_int(value_hex) / 100.0
                    print(f"  {name} ({code}): {value:,.2f}")
                else:
                    print(f"Error: Invalid BCD format for single meter '{name}': {value_hex}")
        else:
            print(f"Warning: Received a short or unknown meter response: {tdata}")

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