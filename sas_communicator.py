import serial
import time
import datetime
import platform
import termios  # For Linux parity control
from crccheck.crc import CrcKermit
from decimal import Decimal

# Helper functions

def decode_to_hex(input_str):
    """Decodes a hex string to a bytearray."""
    return bytearray.fromhex(input_str)

def get_crc(command_hex):
    """Calculates CRC Kermit for a SAS command - EXACTLY like working code."""
    data = decode_to_hex(command_hex)
    crc_instance = CrcKermit()
    crc_instance.process(data)
    crc_hex = crc_instance.finalbytes().hex().upper()
    crc_hex = crc_hex.zfill(4)
    return f"{command_hex}{crc_hex[2:4]}{crc_hex[0:2]}"

def add_left_bcd(number_str, length_bytes):
    """Pads a BCD number string with leading '00' to reach target byte length."""
    number_str = str(int(number_str))
    if len(number_str) % 2 != 0:
        number_str = "0" + number_str
    
    current_len_bytes = len(number_str) / 2
    padding_needed_bytes = length_bytes - current_len_bytes
    
    return "00" * int(padding_needed_bytes) + number_str

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
        """Handle received SAS command - core logic from working code"""
        try:
            if not tdata:
                return
                
            tdata = tdata.replace(" ", "")
            is_processed = 0
            
            print(f"RX SAS: {tdata}")
            
            # Simple responses that confirm communication
            if tdata == "00" or tdata == "01" or tdata == "51":
                is_processed = 1
                print("Simple ACK received")
                return
                
            if tdata == "81" or tdata == "80":
                is_processed = 1
                return
                
            # SAS Version response (0x54)
            if tdata.startswith("0154"):
                is_processed = 1
                self._handle_sas_version_response(tdata)
                return
                
            # Balance query response (0x74)
            if tdata.startswith("0174"):
                is_processed = 1
                self._handle_balance_response(tdata)
                return
                
            # AFT response (0x72)
            if tdata.startswith("0172"):
                is_processed = 1
                self._handle_aft_response(tdata)
                return
                
            # Exception messages (01FF)
            if tdata.startswith("01FF"):
                is_processed = 1
                self._handle_exception_message(tdata)
                return
                
            if not is_processed:
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
            # This would contain balance parsing logic from Yanit_BakiyeSorgulama
            # For now, just log that we got it
            print(f"Balance data: {tdata}")
            
        except Exception as e:
            print(f"Error parsing balance response: {e}")

    def _handle_aft_response(self, tdata):
        """Handle AFT response"""
        try:
            print("AFT response received")
            if len(tdata) >= 14:
                transfer_status = tdata[12:14]
                print(f"AFT Transfer Status: {transfer_status}")
                
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
                    # Remove first 2 bytes (address and status), then get 4 bytes (8 hex chars) for asset number
                    asset_hex = response[2:]
                    # Pad to even length if needed
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