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

    def get_meter(self, meter_code, meter_name):
        """
        Send a SAS meter command and print the result in hex and decimal.
        meter_code: hex string (e.g., '11' for total bet meter)
        meter_name: descriptive name for logging
        """
        command = f"01{meter_code}"
        command = get_crc(command)
        # Send command and wait for response (assume communicator returns hex string response)
        response = self.communicator.sas_send_command_with_queue(meter_name, command, 1, wait_response=True)
        if response:
            # Print full response in hex
            print(f"{meter_name} response (hex): {response}")
            # Parse value (skip header, get 4 bytes for value)
            try:
                value_hex = response[2:10]  # adjust if protocol differs
                value_dec = int(value_hex, 16)
                print(f"{meter_name}: {value_hex} (hex) = {value_dec} (decimal)")
            except Exception as e:
                print(f"Failed to parse {meter_name} meter value: {e}")
        else:
            print(f"No response for {meter_name} meter.")

    def run_all_meters(self):
        """
        Run all main meter reads and print their results.
        Call this after SAS connection is established and asset number is read.
        """
        meters = [
            ("11", "Total Bet Meter"),
            ("12", "Total Win Meter"),
            ("13", "Total In Meter"),
            ("14", "Total Jackpot Meter"),
            ("15", "Games Played Meter"),
            ("16", "Games Won Meter"),
            ("17", "Games Lost Meter"),
            ("1A", "Current Credits Meter"),
        ]
        for code, name in meters:
            self.get_meter(code, name) 