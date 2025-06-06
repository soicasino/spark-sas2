import serial
import time
import datetime
import platform
import termios  # For Linux parity control
from crccheck.crc import CrcKermit
from decimal import Decimal
from card_reader import CardReader  # Import the CardReader class
from sas_money_functions import SasMoney
from billacceptor_functions import BillAcceptorFunctions
from utils import decode_to_hex, get_crc, read_asset_to_int, add_left_bcd

# Helper functions

class SASCommunicator:
    """SAS Communication - Converted to match EXACTLY the working code logic"""
    
    def __init__(self, port_name, global_config, baud_rate=19200, timeout=0.1):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.global_config = global_config
        self.serial_port = None
        self.sas_address = self.global_config.get('sas', 'address', '01')
        self.is_port_open = False
        self.device_type_id = self.global_config.getint('machine', 'devicetypeid', 8)
        
        # CRITICAL: Match working code's global variables
        self.last_sent_poll_type = 81  # Sas_LastSent equivalent
        self.is_communication_by_windows = -1  # G_IsComunicationByWindows
        self.last_80_time = datetime.datetime.now()  # G_Last_80
        self.last_81_time = datetime.datetime.now()  # G_Last_81
        
        # Command queue like working code
        self.pending_command = ""  # GENEL_GonderilecekKomut equivalent
        
        # Initialize platform detection
        if platform.system().startswith("Window"):
            self.is_communication_by_windows = 1
        else:
            self.is_communication_by_windows = 0

        self.card_reader = None  # Will hold CardReader instance
        self.sas_money = SasMoney(self.global_config, self)
        self.bill_acceptor = BillAcceptorFunctions()

    def open_port(self):
        """Opens SAS port - EXACTLY matching working code's OpenCloseSasPort logic"""
        if self.is_port_open:
            return True
            
        try:
            self.serial_port = serial.Serial()
            self.serial_port.port = self.port_name
            self.serial_port.baudrate = self.baud_rate
            self.serial_port.timeout = self.timeout
            
            # CRITICAL: Match working code's serial settings
            self.serial_port.parity = serial.PARITY_NONE
            self.serial_port.stopbits = serial.STOPBITS_ONE
            self.serial_port.bytesize = serial.EIGHTBITS
            self.serial_port.xonxoff = False
            self.serial_port.rtscts = False
            self.serial_port.dsrdtr = False
            
            # CRITICAL: DTR/RTS settings from working code
            self.serial_port.dtr = True
            self.serial_port.rts = False
            
            self.serial_port.open()
            self.is_port_open = True
            
            # CRITICAL: Device type specific initialization like working code
            if self.device_type_id in [1, 4]:  # Novomatic/Octavian
                print("Device type is Novomatic/Octavian, setting parity to EVEN after initial polls.")
                self._send_sas_port("80")
                time.sleep(0.05)
                self._send_sas_port("81")
                self.serial_port.close()
                self.serial_port.parity = serial.PARITY_EVEN
                self.serial_port.open()
                print(f"SAS port {self.port_name} re-opened with EVEN parity.")
            else:
                # Initial poll for other devices
                self._send_sas_port("80")
                time.sleep(0.05)
            
            print(f"SAS port {self.port_name} opened successfully.")
            # Read and print asset number after port is opened
            self.read_and_print_asset_number()
            return True
            
        except serial.SerialException as e:
            print(f"Error opening SAS port {self.port_name}: {e}")
            self.is_port_open = False
            return False

    def close_port(self):
        """Closes the serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_port_open = False
            print(f"SAS port {self.port_name} closed.")

    def _send_sas_port(self, command_hex):
        """Send raw hex to SAS port - EXACTLY like working code's SendSASPORT"""
        if not self.is_port_open or not self.serial_port:
            return
            
        try:
            data_bytes = decode_to_hex(command_hex)
            self.serial_port.write(data_bytes)
            # CRITICAL: Flush input like working code
            # self.serial_port.flushInput()  # Commented in working code
        except Exception as e:
            print(f"Error in _send_sas_port: {e}")

    def send_sas_command(self, command_hex):
        """Send SAS command - EXACTLY matching working code's SendSASCommand"""
        
        command_hex = command_hex.replace(" ", "")
        
        # Update last sent times like working code
        if command_hex == "81":
            self.last_81_time = datetime.datetime.now()
            self.last_sent_poll_type = 81
            
        if command_hex == "80":
            self.last_80_time = datetime.datetime.now()
            self.last_sent_poll_type = 80

        # Log like working code
        if len(command_hex) >= 3:
            print("TX: ", self.device_type_id, command_hex, self.serial_port.port, datetime.datetime.now())

        # CRITICAL: Device type specific sending logic - EXACTLY like working code
        if self.device_type_id == 1 or self.device_type_id == 4:
            # Novomatic/Octavian - just send normally
            self._send_sas_port(command_hex)
        else:
            try:
                # Determine sending method like working code
                is_new_sending_msg = 0
                if self.is_communication_by_windows == 1 or self.device_type_id == 11:
                    is_new_sending_msg = 1
                    
                if self.device_type_id == 6:
                    is_new_sending_msg = 0

                if is_new_sending_msg == 1:  # Windows or Interblock
                    sleeptime = 0.005
                    if self.device_type_id == 11:
                        sleeptime = 0.003
                    
                    # MARK parity for first byte
                    if self.serial_port.parity != serial.PARITY_MARK:
                        self.serial_port.parity = serial.PARITY_MARK
                    self._send_sas_port(command_hex[0:2])
                    time.sleep(sleeptime)
                    
                    # SPACE parity for rest
                    if len(command_hex) > 2:
                        if self.serial_port.parity != serial.PARITY_SPACE:
                            self.serial_port.parity = serial.PARITY_SPACE
                        self._send_sas_port(command_hex[2:])
                        
                else:
                    # Linux with termios - EXACTLY like working code
                    saswaittime = 0.001  # From working code comment: "2020-12-25 test ok gibi.."
                    
                    iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(self.serial_port)
                    
                    CMSPAR = 0x40000000  # EXACTLY like working code
                    
                    # MARK parity for first byte
                    cflag |= termios.PARENB | CMSPAR | termios.PARODD
                    termios.tcsetattr(self.serial_port, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
                    
                    self._send_sas_port(command_hex[0:2])
                    
                    if len(command_hex) > 2:
                        time.sleep(saswaittime)
                        
                        # SPACE parity for rest
                        iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(self.serial_port)
                        cflag |= termios.PARENB
                        cflag &= ~termios.PARODD
                        termios.tcsetattr(self.serial_port, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
                        
                        self._send_sas_port(command_hex[2:])
                        
            except Exception as e:
                print(f"Error in send_sas_command: {e}")

    def get_data_from_sas_port(self, is_message_sent=0):
        """Receive data - EXACTLY like working code's GetDataFromSasPort"""
        if not self.is_port_open or not self.serial_port:
            return ""
            
        try:
            data_left = self.serial_port.in_waiting
            if data_left == 0:
                return ""
            
            out = ''
            read_count_timeout = 3  # From working code
            
            while read_count_timeout > 0:
                read_count_timeout = read_count_timeout - 1
                
                while self.serial_port.in_waiting > 0:
                    out += self.serial_port.read_all().hex()
                    time.sleep(0.005)
            
            return out.upper()
            
        except Exception as e:
            print(f"Error in get_data_from_sas_port: {e}")
            return ""

    def sas_send_command_with_queue(self, command_name, command, do_save_db=0):
        """Send command with queue - EXACTLY like working code's SAS_SendCommand"""
        try:
            # Wait for pending command to clear - EXACTLY like working code
            while len(self.pending_command) > 0:
                time.sleep(0.01)
            
            if len(command) % 2 != 0:
                print("PROBLEM BUYUK!!! Length not even")
                return
                
            self.pending_command = command
            
            # Send immediately like working code
            try:
                self.send_command_if_exists()
            except Exception as e:
                print("Gondermede hata")
                
            # Clear the queue
            self.pending_command = ""
            
        except Exception as e:
            print(f"Error in sas_send_command_with_queue: {e}")

    def send_command_if_exists(self):
        """Send pending command - like working code's SendCommandIsExist"""
        if len(self.pending_command) > 0:
            self.send_sas_command(self.pending_command)

    def send_general_poll(self):
        """Send general poll - alternating 80/81 like working code"""
        if not self.is_port_open:
            return
            
        # Alternate between 80 and 81 like working code
        if self.last_sent_poll_type == 80:
            poll_command = "81"
        else:
            poll_command = "80"
            
        self.send_sas_command(poll_command)

    def request_sas_version(self):
        """Send 0x54 command like working code"""
        command = get_crc("0154")
        self.sas_send_command_with_queue("GetSASVersion", command, 1)

    def request_balance_info(self, lock_code="00", timeout_bcd="9000"):
        """Send 0x74 command like working code"""
        command_body = f"74{lock_code}{timeout_bcd}"
        command = get_crc(self.sas_address + command_body)
        self.sas_send_command_with_queue("RequestBalanceInfo", command, 1)

    def parse_message(self, message):
        """Parse received message - EXACTLY like working code's ParseMessage"""
        if not message:
            return None, None, None, 0
            
        message_found = ""
        message_found_crc = ""
        message_rest_of_message = ""
        message_important = 0
        
        # Check if length exists - EXACTLY like working code
        is_length_exist = 0
        if (message[0:4] == "0172" or message[0:4] == "0174" or 
            message[0:4] == "012F" or message[0:4] == "0154" or message[0:4] == "01AF"):
            is_length_exist = 1
        
        if is_length_exist == 1:
            message_important = 1
            message_length = (int(message[4:6], 16) * 2)
            
            message_found = message[0:message_length + 6 + 4]
            message_found_crc = message[message_length + 6:message_length + 6 + 4]
            message_rest_of_message = message[message_length + 6 + 4:len(message)]
            
        else:  # Messages without length
            if message[0:4] == "01FF":
                message_important = 1
                message_length = 2
                
                message_found = message[4:6]
                
                # Specific message types like working code
                if message_found == "4F":  # Bill accepted
                    message_length = 8
                if message_found == "69":  # AFT TRANSFER COMPLETED
                    message_length = 2
                if message_found == "7C":  # Legacy bonus pay
                    message_length = 12
                if message_found == "7E":  # Game started
                    message_length = 10
                if message_found == "7F":  # Game end
                    message_length = 6
                if message_found == "88":  # Reel stopped
                    message_length = 4
                if message_found == "8A":  # Game recall entered
                    message_length = 6
                if message_found == "8B":  # Card held
                    message_length = 3
                if message_found == "8C":  # Game selected
                    message_length = 4
                
                message_length = ((message_length + 1) * 2)
                message_found = message[0:message_length + 4]
                message_found_crc = message[message_length:message_length + 4]
                try:
                    message_rest_of_message = message[message_length + 4 + 4:len(message)]
                except:
                    print("Parse error at 01FF")
            else:
                message_length = len(message)
                message_found = message[0:message_length]
                message_found_crc = message[message_length - 4:message_length]
        
        return message_found, message_found_crc, message_rest_of_message, message_important

    def handle_received_sas_command(self, tdata):
        """Comprehensive SAS response handler, covering all message types from the reference."""
        try:
            if not tdata:
                return
            tdata = tdata.replace(" ", "").upper()

            # Early returns for simple ACKs and known short responses
            early_acks = {
                "01FF838F13": "Ignore: known message",
                "01FF001CA501FF001CA5": "Ignore: known message",
                "01FF001CA501": "Ignore: known message",
                "81": "Simple ACK",
                "01FF820602": "Display meters or attendant menu has been entered",
                "01FF201E84": "General tilt",
                "0101FF001CA5": "Ignore: known message",
            }
            if tdata in early_acks:
                print(early_acks[tdata])
                return
            if tdata[0:6] == "01FF1F":
                print("send gaming machine id - information")
                return

            # Dispatch table for exact and prefix matches
            dispatch = [
                (lambda d: d.startswith("01FF7C"), lambda d: print("Legacy bonus pay")),
                (lambda d: d.startswith("01FF6B"), lambda d: print("AFT request for host to cash out win")),
                (lambda d: d.startswith("01FF6C"), lambda d: print("AFT request to register")),
                (lambda d: d.startswith("011B"), lambda d: print("HandpayInformation")),
                (lambda d: d.startswith("0153"), lambda d: print("GameConfiguration")),
                (lambda d: d.startswith("01731D"), lambda d: print("Register Gaming Machine Response")),
                (lambda d: d.startswith("01FF6FED3E"), lambda d: print("Game locked")),
                (lambda d: d[0:10] == "01FF5110E6", lambda d: print("Handpay is pending")),
                (lambda d: d[0:10].startswith("01FF52"), lambda d: print("Handpay was reset")),
                (lambda d: d[0:4] == "012F" or d[0:4] == "01AF", lambda d: print("MeterAll")),
                (lambda d: d[0:4] == "0172", lambda d: print("AFT response")),
                (lambda d: d[0:4] == "0174", lambda d: print("Balance query response")),
                (lambda d: d.startswith("01FF54BDB1"), lambda d: print("Progressive win")),
                (lambda d: d == "01FF29DF19", lambda d: print("Bill acceptor hardware failure!")),
                (lambda d: d == "00", lambda d: print("Simple ACK")),
                (lambda d: d == "01", lambda d: print("Simple ACK")),
                (lambda d: d == "51", lambda d: print("Simple ACK")),
                (lambda d: d.startswith("01FF69DB5B") or d == "FF69DB5B" or d == "69DB5B" or d == "69", lambda d: print("AFT Transfer is completed")),
                (lambda d: "01FF66" in d, lambda d: print("Cashout is pressed or Hopper Limit Reached")),
                (lambda d: d[0:6] == "01FF8A", lambda d: print("Game Recall Entry Displayed")),
                (lambda d: d[0:4] == "0156", lambda d: print("EnabledGameNumbers")),
                (lambda d: d[0:6] == "01FF6A" or "01FF6A4069" in d, lambda d: print("AFT Request for host cashout")),
                (lambda d: d[0:2] == "87", lambda d: print("Gaming machine unable to perform transfers at this time")),
                (lambda d: d[0:4] == "011F" and len(d) > 10, lambda d: print("Send gaming machine ID & information")),
                (lambda d: d[0:6] == "019400", lambda d: print("Handpay is reseted")),
                (lambda d: d[0:4] == "0154", lambda d: self._handle_sas_version_response(d)),
                (lambda d: d == "1F", lambda d: print("Simple ACK")),
                (lambda d: d == "01FF001CA5" or d == "01FF1F6A4D" or d == "01FF709BD6", lambda d: print("Real time reporting")),
                (lambda d: d[0:6] == "01FF88", lambda d: print("Reel N has stopped")),
                (lambda d: d[0:4] == "01B5", lambda d: print("Game Info")),
                (lambda d: d[0:6] == "01FF8C", lambda d: print("Game selected")),
            ]
            for cond, action in dispatch:
                try:
                    if cond(tdata):
                        action(tdata)
                        return
                except Exception as e:
                    print(f"Error in dispatch for SAS message: {e}")

            # Asset number response (0x73)
            if tdata.startswith("0173"):
                asset_hex = tdata[8:16]
                if len(asset_hex) % 2 != 0:
                    asset_hex = '0' + asset_hex
                reversed_hex = ''.join([asset_hex[i:i+2] for i in range(len(asset_hex)-2, -2, -2)])
                asset_dec = int(reversed_hex, 16)
                print(f"[ASSET NO] HEX: {asset_hex}  DEC: {asset_dec}")
                # Call meter reading after asset number is read
                self.sas_money.run_all_meters()
                return
            # SAS Version response (0x54) (fallback)
            if tdata.startswith("0154"):
                self._handle_sas_version_response(tdata)
                return
            # Balance query response (0x74) (fallback)
            if tdata.startswith("0174"):
                self._handle_balance_response(tdata)
                return
            # AFT response (0x72) (fallback)
            if tdata.startswith("0172"):
                self._handle_aft_response(tdata)
                return
            # Exception messages (01FF) (fallback)
            if tdata.startswith("01FF"):
                self._handle_exception_message(tdata)
                return
            print(f"Unhandled SAS message: {tdata}")
        except Exception as e:
            print(f"Error in handle_received_sas_command: {e}")

    def _handle_sas_version_response(self, tdata):
        """Handle SAS version response"""
        try:
            print("SAS Version response received")
            if len(tdata) >= 10:
                sas_version = tdata[6:12]  # 3 bytes for version
                print(f"SAS Version: {sas_version}")
                
                # Serial number is the rest
                serial_data = tdata[12:-4]  # Exclude CRC
                print(f"Serial Number data: {serial_data}")
                
        except Exception as e:
            print(f"Error parsing SAS version: {e}")

    def _handle_balance_response(self, tdata):
        """Handle balance query response"""
        try:
            print("Balance response received")
            self.sas_money.yanit_bakiye_sorgulama(tdata)
        except Exception as e:
            print(f"Error parsing balance response: {e}")

    def _handle_aft_response(self, tdata):
        """Handle AFT response"""
        try:
            print("AFT response received")
            # TODO: Use self.sas_money for AFT parsing/logic
        except Exception as e:
            print(f"Error parsing AFT response: {e}")

    def _handle_exception_message(self, tdata):
        """Handle exception messages (01FF)"""
        try:
            if len(tdata) >= 6:
                exception_code = tdata[4:6]
                print(f"Exception code: {exception_code}")
                
                # Specific exceptions like working code
                if tdata == "01FF69DB5B":
                    print("AFT Transfer is completed")
                elif tdata.startswith("01FF7E"):
                    print("Game started")
                elif tdata.startswith("01FF7F"):
                    print("Game ended")
                elif tdata.startswith("01FF6A"):
                    print("AFT request for host cashout")
                    
        except Exception as e:
            print(f"Error parsing exception message: {e}")

    def read_and_print_asset_number(self):
        """Read asset number from SAS and print it to screen."""
        try:
            command = self.sas_address + '7301FF'
            command_crc = get_crc(command)
            self.sas_send_command_with_queue('ReadAssetNo', command_crc, 0)
            for _ in range(10):
                time.sleep(0.2)
                response = self.get_data_from_sas_port()
                if response and response.startswith('0173'):
                    asset_hex = response[8:16]
                    if len(asset_hex) % 2 != 0:
                        asset_hex = '0' + asset_hex
                    # Reverse by bytes
                    reversed_hex = ''.join([asset_hex[i:i+2] for i in range(len(asset_hex)-2, -2, -2)])
                    asset_dec = int(reversed_hex, 16)
                    print(f"[ASSET NO] HEX: {asset_hex}  DEC: {asset_dec}")
                    return
            print("[ASSET NO] Could not read asset number from SAS.")
        except Exception as e:
            print(f"[ASSET NO] Error reading from SAS: {e}")

    def find_ports_with_card_reader(self, port_list):
        """
        Example integration: Find and open card reader port from a list of ports.
        """
        self.card_reader = CardReader()
        found = self.card_reader.find_port(port_list)
        if found:
            print(f"Card reader integrated on port: {self.card_reader.port_name}")
            self.card_reader.start_polling()  # Start background polling for cards
        else:
            print("No card reader found during port scan.")

    def find_ports_and_read_card_if_present(self, port_list):
        """
        Find SAS port (assume already handled), then find card reader port.
        If card reader is found, start polling for cards.
        """
        print("[SAS] SAS port finding assumed handled (open_port or similar).")
        print("[SAS] Now searching for card reader port...")
        self.find_ports_with_card_reader(port_list)
        if self.card_reader and self.card_reader.is_card_reader_opened:
            print("[SAS] Card reader found and polling started.")
        else:
            print("[SAS] No card reader found.")

        if not any(p.get('port_no') == '/dev/ttyUSB0' or p.get('port') == '/dev/ttyUSB0' for p in port_list):
            port_list.append({'port_no': '/dev/ttyUSB0', 'is_used': 0, 'device_name': ''})
        print(f"[DEBUG] Port list for card reader: {port_list}")

    # --- Money command wrappers ---
    def money_balance_query(self, sender, isforinfo, sendertext='UndefinedBakiyeSorgulama'):
        return self.sas_money.komut_bakiye_sorgulama(sender, isforinfo, sendertext)

    def money_cash_in(self, doincreasetransactionid, transfertype, customerbalance, customerpromo, transactionid, assetnumber, registrationkey):
        return self.sas_money.komut_para_yukle(doincreasetransactionid, transfertype, customerbalance, customerpromo, transactionid, assetnumber, registrationkey)

    def money_cash_out(self, doincreaseid, transactionid, assetnumber, registrationkey):
        return self.sas_money.komut_para_sifirla(doincreaseid, transactionid, assetnumber, registrationkey)

    def money_cancel_aft_transfer(self):
        return self.sas_money.komut_cancel_aft_transfer()

    def test_read_all_meters(self, meter_type='basic', game_id=None):
        """Send a one-time SAS command to read meters for test purposes.
        meter_type: 'basic', 'extended', 'bill', 'game'
        game_id: required for 'game' type
        """
        if meter_type == 'basic':
            print("[SAS TEST] Sending one-time read ALL BASIC meters command (012F0C0000)...")
            command = get_crc("012F0C0000")
        elif meter_type == 'extended':
            print("[SAS TEST] Sending one-time read EXTENDED meters command (01AF...)")
            # Example extended meters command (commonly used set)
            command = get_crc("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600")
        elif meter_type == 'bill':
            print("[SAS TEST] Sending one-time read BILL meters command (011E)...")
            command = get_crc("011E")
        elif meter_type == 'game':
            if game_id is None:
                print("[SAS TEST] Game ID required for game meters!")
                return
            print(f"[SAS TEST] Sending one-time read GAME meters command (0152) for game_id={game_id}...")
            # 0152 + game_id (2 bytes, BCD)
            game_id_bcd = f"{int(game_id):04X}"  # 2 bytes, hex
            command = get_crc(f"0152{game_id_bcd}")
        else:
            print(f"[SAS TEST] Unknown meter_type: {meter_type}")
            return
        self.sas_send_command_with_queue(f"TestReadMeters_{meter_type}", command, 0) 