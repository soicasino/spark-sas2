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

    def get_meter(self, isall=0, sender="Unknown", gameid=0):
        print("=== METER: get_meter called ===")
        print(f"METER: get_meter params: isall={isall}, sender={sender}, gameid={gameid}")
        L_OperationStartDate_Meter = datetime.datetime.now()
        self.is_waiting_for_meter = True
        self.komut_get_meter(isall, gameid)
        retry_count = 0
        while self.is_waiting_for_meter and retry_count < 10:
            print(f"METER: get_meter waiting, retry_count={retry_count}")
            time.sleep(1.5)
            retry_count += 1
            if self.is_waiting_for_meter:
                print(f"METER: get_meter retrying komut_get_meter, retry_count={retry_count}")
                self.komut_get_meter(isall, gameid)
        if not self.is_waiting_for_meter:
            print("METER: get_meter meter is received")
        else:
            print("METER: get_meter timeout waiting for meter response")
        print(f"METER: get_meter process completed in {datetime.datetime.now() - L_OperationStartDate_Meter}")
        print("=== METER: get_meter end ===")

    def run_all_meters(self):
        print("DEBUG: run_all_meters START")
        self.get_meter(isall=0)
        print("DEBUG: run_all_meters END")

    def is_valid_bcd(self, hex_str):
        """Check if a hex string is valid BCD (only 0-9 digits)."""
        return all(c in '0123456789' for c in hex_str)

    # Mapping of meter codes to names and value lengths (in bytes)
    METER_CODE_MAP = {
        'A0': ('total_coin_in', 4),
        'B8': ('total_coin_out', 4),
        '02': ('total_jackpot', 4),
        '03': ('total_handpay', 4),
        '0B': ('bills_accepted', 4),
        'A2': ('non_cashable_in', 4),
        'BA': ('non_cashable_out', 4),
        '1E': ('total_bonus', 4),
        '04': ('total_cancelled_credits', 4),
        '05': ('games_played', 4),
        '06': ('games_won', 4),
        '0C': ('current_credits', 4),
        '7F': ('weighted_avg_payback', 4),
        'FA': ('regular_cashable_keyed', 4),
        'FB': ('restricted_keyed', 4),
        'FC': ('nonrestricted_keyed', 4),
        '1D': ('machine_paid_progressive', 4),
        '17': ('total_electronic_in', 4),
        '18': ('total_electronic_out', 4),
        '15': ('total_ticket_in', 4),
        '16': ('total_ticket_out', 4),
        '23': ('total_handpaid_credits', 4),
        # Add more as needed
    }

    def handle_single_meter_response(self, tdata):
        """Dynamically parse and print a meter block or single meter response, robustly."""
        # If the response is a block (long), parse by code/length
        if len(tdata) > 40:
            print("--- SAS Meter Block (Dynamic Parse) ---")
            idx = 6  # skip address (2), code (2), length (2)
            parsed = {}
            while idx + 2 <= len(tdata):
                code = tdata[idx:idx+2]
                idx += 2
                if code not in self.METER_CODE_MAP:
                    # Unknown code, try to skip 4 bytes and continue
                    print(f"Unknown meter code: {code}, skipping 4 bytes")
                    idx += 8
                    continue
                name, nbytes = self.METER_CODE_MAP[code]
                hex_len = nbytes * 2
                value_hex = tdata[idx:idx+hex_len]
                idx += hex_len
                if len(value_hex) < hex_len:
                    print(f"{name}: (no data)")
                    continue
                if self.is_valid_bcd(value_hex):
                    value = int(value_hex, 16) / 100.0
                    print(f"{name}: {value:,.2f}")
                    parsed[name] = value
                else:
                    print(f"{name}: INVALID BCD ({value_hex})")
            print("----------------------")
        else:
            # Fallback: single meter response
            if len(tdata) < 10:
                print(f"Response too short: {tdata}")
                return
            code = tdata[2:4]
            value_hex = tdata[6:14]  # 4 bytes (8 hex chars) after len
            name = self.METER_CODE_MAP.get(code, (f"meter_{code}", 4))[0]
            if self.is_valid_bcd(value_hex):
                value = int(value_hex, 16) / 100.0
                print(f"{name}: {value:,.2f}")
            else:
                print(f"{name}: INVALID BCD ({value_hex})") 