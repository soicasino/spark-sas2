import serial
import time
import datetime
import platform
import os
import subprocess
import threading
import termios  # For Linux parity control
from crccheck.crc import CrcKermit
import configparser
from decimal import Decimal

class ConfigManager:
    def __init__(self, config_file="settings.ini"):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            print(f"Warning: Config file {config_file} not found. Using defaults.")
            self._create_default_config()
        else:
            self.config.read(config_file)

    def _create_default_config(self):
        if not self.config.has_section('sas'):
            self.config.add_section('sas')
        self.config.set('sas', 'address', '01')
        self.config.set('sas', 'assetnumber', '00000000')
        self.config.set('sas', 'registrationkey', '0000000000000000000000000000000000000000')

        if not self.config.has_section('machine'):
            self.config.add_section('machine')
        self.config.set('machine', 'devicetypeid', '8')

    def get(self, section, option, fallback=None):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return fallback

    def getint(self, section, option, fallback=0):
        if self.config.has_option(section, option):
            try:
                return self.config.getint(section, option)
            except ValueError:
                return fallback
        return fallback

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


class PortManager:
    """Port detection and management"""
    
    def __init__(self):
        self.available_ports = []

    def find_ports_linux(self):
        """Find available ports on Linux"""
        self.available_ports = []
        try:
            # Try USB ports first
            result = subprocess.run(['ls', '/dev/ttyUSB*'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                ports = result.stdout.strip().split('\n')
                for port in ports:
                    if port:
                        self.available_ports.append({
                            'port_no': port,
                            'is_used': False,
                            'device_name': ''
                        })
            
            # If no USB ports, try serial ports
            if not self.available_ports:
                result = subprocess.run(['ls', '/dev/ttyS*'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    ports = result.stdout.strip().split('\n')
                    for port in ports:
                        if port:
                            self.available_ports.append({
                                'port_no': port,
                                'is_used': False,
                                'device_name': ''
                            })
                            
        except Exception as e:
            print(f"Error finding ports: {e}")
            
        print(f"Found ports: {self.available_ports}")
        return self.available_ports

    def find_sas_port(self, config):
        """Find SAS port by testing communication - like working code's FindPortForSAS"""
        print("<FIND SAS PORT>-----------------------------------------------------------------")
        
        if not self.available_ports:
            self.find_ports_linux()
            
        for port_info in self.available_ports:
            if not port_info['is_used']:
                port_name = port_info['port_no']
                print(f"Testing SAS on port: {port_name}")
                
                # Try different device types like working code
                for device_type in [8, 1, 2]:  # Try default first, then Novomatic types
                    config.config.set('machine', 'devicetypeid', str(device_type))
                    
                    sas_comm = SASCommunicator(port_name, config)
                    if sas_comm.open_port():
                        print(f"Port {port_name} opened, testing communication...")
                        
                        # Test communication
                        found_sas = False
                        for attempt in range(10):  # 10 attempts like working code
                            sas_comm.request_sas_version()
                            time.sleep(0.1)
                            
                            response = sas_comm.get_data_from_sas_port()
                            if response and ("0154" in response or len(response) > 6):
                                print(f"SAS found on port {port_name} with device type {device_type}")
                                found_sas = True
                                break
                                
                            time.sleep(0.05)
                        
                        sas_comm.close_port()
                        
                        if found_sas:
                            port_info['is_used'] = True
                            port_info['device_name'] = 'sas'
                            print("</FIND SAS PORT>-----------------------------------------------------------------")
                            return port_name, device_type
                            
                print(f"No SAS found on port {port_name}")
        
        print("No SAS port found!")
        print("</FIND SAS PORT>-----------------------------------------------------------------")
        return None, None


class SlotMachineApplication:
    """Main application - simplified for SAS communication testing"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.port_mgr = PortManager()
        self.sas_comm = None
        self.running = False
        self.sas_poll_timer = None

    def initialize_sas(self):
        """Initialize SAS communication"""
        print("Initializing SAS communication...")
        
        # Find SAS port
        sas_port, device_type = self.port_mgr.find_sas_port(self.config)
        
        if sas_port:
            print(f"Using SAS port: {sas_port}, device type: {device_type}")
            self.config.config.set('machine', 'devicetypeid', str(device_type))
            
            self.sas_comm = SASCommunicator(sas_port, self.config)
            if self.sas_comm.open_port():
                print("SAS communication initialized successfully!")
                return True
            else:
                print("Failed to open SAS port")
                return False
        else:
            print("No SAS port found")
            return False

    def sas_polling_loop(self):
        """SAS polling loop"""
        if not self.running or not self.sas_comm or not self.sas_comm.is_port_open:
            return
        
        # Send poll
        self.sas_comm.send_general_poll()
        
        # Check for response
        time.sleep(0.05)  # Give time for response
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        # Schedule next poll
        if self.running:
            self.sas_poll_timer = threading.Timer(0.04, self.sas_polling_loop)  # 40ms like working code
            self.sas_poll_timer.daemon = True
            self.sas_poll_timer.start()

    def test_sas_commands(self):
        """Test basic SAS commands"""
        if not self.sas_comm:
            print("SAS not initialized")
            return
            
        print("Testing SAS commands...")
        
        # Test SAS version
        print("Requesting SAS version...")
        self.sas_comm.request_sas_version()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        time.sleep(1)
        
        # Test balance query
        print("Requesting balance info...")
        self.sas_comm.request_balance_info()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)

    def start(self):
        """Start the application"""
        print("Starting Slot Machine Application...")
        
        if not self.initialize_sas():
            print("Failed to initialize SAS. Exiting.")
            return
        
        self.running = True
        
        # Test some commands
        self.test_sas_commands()
        
        # Start polling
        self.sas_polling_loop()
        
        print("Application started. Press Ctrl+C to exit.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutdown requested.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown the application"""
        print("Shutting down...")
        self.running = False
        
        if self.sas_poll_timer:
            self.sas_poll_timer.cancel()
        
        if self.sas_comm:
            self.sas_comm.close_port()
        
        print("Shutdown complete.")


if __name__ == "__main__":
    # Run the application
    app = SlotMachineApplication()
    app.start()