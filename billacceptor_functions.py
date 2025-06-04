import datetime
import time
from decimal import Decimal

class BillAcceptorFunctions:
    def __init__(self):
        self.g_last_game_ended = datetime.datetime.now()
        self.g_last_bill_acceptor_ackapa_command = datetime.datetime.now()
        self.is_billacceptor_open = 0
        self.g_machine_bill_acceptor_type_id = 1  # Set this as needed
        self.g_online_is_online_playing = 0
        self.is_bill_acceptor_pooling_started = 0
        self.bill_acceptor_command_str = ""
        self.count_status_check = 0
        self.dict_currencies = []
        # External dependencies (must be set from outside)
        self.billacceptorport = None
        # The following must be set from outside as well:
        # self.SQL_Safe_InsImportantMessage, self.GetMeiACK, self.Decode2Hex

    def billacceptor_open_thread(self, sender):
        last_game_ended_diff = (datetime.datetime.now() - self.g_last_game_ended).total_seconds()
        self.bill_acceptor_inhibit_open()

    def bill_acceptor_game_ended(self):
        last_game_ended_diff = (datetime.datetime.now() - self.g_last_game_ended).total_seconds()
        self.bill_acceptor_inhibit_open()
        # threading logic omitted

    def bill_acceptor_game_started(self):
        last_game_ended_diff = (datetime.datetime.now() - self.g_last_game_ended).total_seconds()
        self.bill_acceptor_inhibit_close()

    def bill_acceptor_inhibit_open(self):
        self.is_billacceptor_open = 1
        last_bill_ac_diff = (datetime.datetime.now() - self.g_last_bill_acceptor_ackapa_command).total_seconds()
        self.g_last_bill_acceptor_ackapa_command = datetime.datetime.now()
        if self.g_machine_bill_acceptor_type_id == 1:
            self.send_bill_acceptor_command("FC06C30004D6")
        if self.g_machine_bill_acceptor_type_id == 2:
            self.send_bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 7F 1C 10 03 6A"))

    def bill_acceptor_inhibit_close(self):
        self.is_billacceptor_open = 0
        last_bill_ac_diff = (datetime.datetime.now() - self.g_last_bill_acceptor_ackapa_command).total_seconds()
        self.g_last_bill_acceptor_ackapa_command = datetime.datetime.now()
        if self.g_machine_bill_acceptor_type_id == 1:
            self.send_bill_acceptor_command("FC06C3018DC7")
        if self.g_machine_bill_acceptor_type_id == 2:
            self.send_bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 00 1C 10 03 14"))
        print("Disable bill acceptor")

    def bill_acceptor_reset(self):
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 40 2B 15")
        if self.g_machine_bill_acceptor_type_id == 2:
            self.bill_acceptor_command("02 08 60 7F 7F 7F 03 17")

    def bill_acceptor_reject(self, sender):
        self.sql_safe_ins_important_message("Bill is rejected " + sender, 80)
        print("****** REJECT YAP ******")
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 43 B0 27")
        if self.g_machine_bill_acceptor_type_id == 2:
            self.bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 7F 5C 10 03 00"))

    def bill_acceptor_status_check(self):
        self.count_status_check += 1
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 11 27 56")
        if self.g_machine_bill_acceptor_type_id == 2:
            if self.is_billacceptor_open == 1:
                self.bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 7F 1C 10 03 00"))
            if self.is_billacceptor_open == 0:
                self.bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 00 1C 10 03 00"))

    def bill_acceptor_stack1(self):
        self.sql_safe_ins_important_message("Bill Stack Cmd", 100)
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 41 A2 04")
        if self.g_machine_bill_acceptor_type_id == 2:
            self.bill_acceptor_command(self.get_mei_msg_crc("02 08 " + self.get_mei_ack() + " 7F 3C 10 03 00"))

    def bill_acceptor_currency_assign_req(self):
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 8A 7D 7C")
        if self.g_machine_bill_acceptor_type_id == 2:
            print("Bisi yapmaya gerek yok currency assign")

    def bill_acceptor_ack(self):
        if self.g_machine_bill_acceptor_type_id == 1:
            self.bill_acceptor_command("FC 05 50 AA 05")

    def bill_acceptor_command(self, data):
        if self.is_bill_acceptor_pooling_started == 0:
            return
        if self.g_online_is_online_playing == 1:
            return
        data = data.replace(" ", "")
        if "ACK" in data:
            data = data.replace("ACK", self.get_mei_ack())
        if "CRC" in data:
            data = data.replace("CRC", "")
            data = self.get_mei_msg_crc(data)
            print("senddata", data)
        country_try = 0
        while len(self.bill_acceptor_command_str) > 0:
            country_try += 1
            if country_try % 10 == 0:
                print("Please wait.. Another command is being sent to bill acceptor Old", self.bill_acceptor_command_str, "Current", data)
            time.sleep(0.1)
            if country_try > 5000:
                print("break bill acceptor while commandstr")
                break
        self.bill_acceptor_command_str = data

    def send_bill_acceptor_command(self, senddata):
        try:
            try:
                senddata = senddata.replace(" ", "")
                if "ACK" in senddata:
                    senddata = senddata.replace("ACK", self.get_mei_ack())
                if "CRC" in senddata:
                    senddata = senddata.replace("CRC", "")
                    senddata = self.get_mei_msg_crc(senddata)
                    print("senddata", senddata)
            except Exception as esql1:
                print("Err")
            is_show_debug_sent = 0
            if is_show_debug_sent == 1:
                print("Gonderilen mesaj", senddata)
            hex_data = self.decode2hex(senddata)
            self.billacceptorport.write(hex_data)
        except Exception as esql:
            senddata = ""

    def send_bill_acceptor_command_is_exist(self):
        if len(self.bill_acceptor_command_str) == 0:
            return
        try:
            senddata = self.bill_acceptor_command_str.replace(" ", "")
            is_show_debug_sent = 1
            if senddata == "020811001C100315":
                is_show_debug_sent = 0
            if senddata == "020810001C100314":
                is_show_debug_sent = 0
            if senddata == "0208107F1C10036B":
                is_show_debug_sent = 0
            if senddata == "0208117F1C10036A":
                is_show_debug_sent = 0
            is_show_debug_sent = 0
            if is_show_debug_sent == 1:
                print("Gonderilen mesaj", senddata)
            hex_data = self.decode2hex(senddata)
            self.billacceptorport.write(hex_data)
        except Exception as esql:
            self.bill_acceptor_command_str = ""
        self.bill_acceptor_command_str = ""

    def get_mei_msg_crc(self, orji):
        orji = orji.replace(" ", "")
        orji = orji[0:len(orji) - 2] + "00"
        hex_data = self.decode2hex(orji)
        for byte in range(1, len(hex_data) - 2):
            hex_data[len(hex_data) - 1] ^= hex_data[byte]
        tdata = hex_data.hex().upper()
        return tdata

    def parse_mei_currency(self, money_string):
        ext_data_index = 20
        currency_code = money_string[ext_data_index:ext_data_index + 2]
        country_code = money_string[ext_data_index + 2:ext_data_index + 2 + 6]
        country_code_hex = money_string[ext_data_index + 2:ext_data_index + 2 + 6]
        country_code = bytearray.fromhex(country_code).decode()
        if country_code_hex == "000000":
            return "", "", 0
        bill_value = money_string[ext_data_index + 8:ext_data_index + 8 + 6]
        bill_value = int(bytearray.fromhex(bill_value).decode())
        num3 = money_string[ext_data_index + 16:  ext_data_index + 16 + 4]
        num3 = int(bytearray.fromhex(num3).decode())
        carpan = money_string[ext_data_index + 14:ext_data_index + 14 + 2]
        if carpan == "2B":
            num4 = 1
            while True:
                if num4 > num3:
                    break
                bill_value = bill_value * 10
                num4 = num4 + 1
        else:
            num5 = 1
            while True:
                if num5 > num3:
                    break
                bill_value = bill_value / 10
                num5 = num5 + 1
        return currency_code, country_code, bill_value

    def get_currency_denom(self, currency_code):
        if len(self.dict_currencies) == 0:
            return -1
        for member in self.dict_currencies:
            if str(member['currencyCode']) == str(currency_code):
                return member["denom"]
        return -1

    def get_currency_country_code(self, currency_code):
        if len(self.dict_currencies) == 0:
            return "-1"
        for member in self.dict_currencies:
            if str(member['currencyCode']) == str(currency_code):
                return member["countryCode"]
        return "-1"

    def get_currency_denom_hex(self, currency_code):
        if len(self.dict_currencies) == 0:
            return "-1"
        for member in self.dict_currencies:
            if str(member['currencyCode']) == str(currency_code):
                return member["denomHex"]
        return "-1"

    # The following methods must be set from outside or implemented:
    def sql_safe_ins_important_message(self, msg, code):
        # Placeholder: implement or set from outside
        pass

    def get_mei_ack(self):
        # Placeholder: implement or set from outside
        return "00"

    def decode2hex(self, s):
        # Placeholder: implement or set from outside
        return bytearray.fromhex(s) 