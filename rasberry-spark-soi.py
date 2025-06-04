import serial
import time
import datetime
import platform
import os
import fnmatch
import subprocess
import re
import pymssql # For type hinting, actual DB calls would be in a DBManager
import sqlite3 # For type hinting
from crccheck.crc import CrcKermit
import configparser
import ctypes # For CRT288B Card Reader
import threading # For placeholder, original threading logic needs careful integration
from decimal import Decimal

class ConfigManager:
    def __init__(self, config_file_path="settings.ini"):
        self.config = configparser.ConfigParser()
        self.config_file_path = config_file_path
        self.logger = print # Replace with a proper logger

    def _create_default_config_sections(self):
        default_sections = ['sas', 'machine', 'cardreader', 'billacceptor', 'payment']
        for section in default_sections:
            if not self.config.has_section(section):
                self.config.add_section(section)

    def apply_operational_defaults(self):
        self._create_default_config_sections()
        self.set_value('sas', 'address', self.get('sas', 'address', '01'))
        self.set_value('sas', 'assetnumber', self.get('sas', 'assetnumber', '00000000'))
        self.set_value('sas', 'registrationkey', self.get('sas', 'registrationkey', '0000000000000000000000000000000000000000'))
        self.set_value('machine', 'devicetypeid', str(self.getint('machine', 'devicetypeid', 8)))
        self.set_value('machine', 'config_is_cashout_soft', str(self.getint('machine', 'config_is_cashout_soft', 0)))
        self.set_value('cardreader', 'type', str(self.getint('cardreader', 'type', 2)))
        self.set_value('cardreader', 'lib_path', self.get('cardreader', 'lib_path', './crt_288B_UR.so'))
        self.set_value('billacceptor', 'typeid', str(self.getint('billacceptor', 'typeid', 0)))
        self.set_value('payment', 'transactionid', str(self.getint('payment', 'transactionid', 0)))
        self.logger("Applied operational default configurations.")

    def get(self, section, option, fallback=None):
        if self.config.has_option(section, option): return self.config.get(section, option)
        return fallback
    def getint(self, section, option, fallback=0):
        if self.config.has_option(section, option):
            try: return self.config.getint(section, option)
            except ValueError: return fallback
        return fallback
    def getdecimal(self, section, option, fallback=Decimal('0.0')):
        if self.config.has_option(section, option):
            try: return Decimal(self.config.get(section, option))
            except Exception: return fallback
        return fallback
    def set_value(self, section, option, value):
        if not self.config.has_section(section): self.config.add_section(section)
        if value is not None: self.config.set(section, option, str(value))
        elif self.config.has_option(section, option): self.config.remove_option(section, option)
    def save(self):
        try:
            with open(self.config_file_path, 'w') as configfile: self.config.write(configfile)
            self.logger(f"Configuration saved to {self.config_file_path}")
        except Exception as e: self.logger(f"Error saving config file to {self.config_file_path}: {e}")

def decode_to_hex(input_str): return bytearray.fromhex(input_str)
def get_crc(command_hex_with_addr): # Expects command to already have SAS address prefixed
    data = decode_to_hex(command_hex_with_addr)
    crc_instance = CrcKermit(); crc_instance.process(data)
    crc_hex = crc_instance.finalbytes().hex().upper().zfill(4)
    return f"{command_hex_with_addr}{crc_hex[2:4]}{crc_hex[0:2]}" # SAS CRC is low byte then high byte

def add_left_bcd(number_str, length_bytes):
    number_str = str(int(number_str))
    if len(number_str) % 2 != 0: number_str = "0" + number_str
    padding_needed_bytes = length_bytes - (len(number_str) / 2)
    return "00" * int(padding_needed_bytes) + number_str
def hex_to_int(hex_str):
    try: return bytes.fromhex(hex_str).decode('ascii', errors='ignore')
    except UnicodeDecodeError: return int(hex_str, 16)
    except ValueError: return hex_str

class PortManager:
    def __init__(self, config_manager_instance):
        self.config_manager = config_manager_instance
        self.available_ports = []
        self.sas_port_name = None
        self.card_reader_port_name = None
        self.bill_acceptor_port_name = None
        self.logger = self.config_manager.logger

    def _execute_linux_command(self, command):
        try:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate(timeout=5)
            if error: self.logger(f"Error executing '{command}': {error.decode(errors='ignore')}")
            return output.decode(errors='ignore')
        except subprocess.TimeoutExpired: self.logger(f"Timeout executing command: {command}"); return ""
        except FileNotFoundError: self.logger(f"Command '{command.split()[0]}' not found."); return ""
        except Exception as e: self.logger(f"Exception executing '{command}': {e}"); return ""

    def find_available_serial_ports(self):
        self.available_ports = []
        self.logger("Finding available serial ports...")
        if platform.system().startswith("Window"):
            try:
                import serial.tools.list_ports
                ports = serial.tools.list_ports.comports()
                for port in ports: self.available_ports.append({"port_no": port.device, "is_used": False, "device_name": ""})
            except ImportError: self.logger("pyserial list_ports not available.")
            except Exception as e: self.logger(f"Error listing Windows COM ports: {e}")
            if not self.available_ports: self.available_ports.append({"port_no": "COM4", "is_used": False, "device_name": ""}) # Fallback
        elif platform.system().startswith("Linux"):
            patterns = ["/dev/ttyUSB*", "/dev/ttyS*", "/dev/ttyACM*"]
            for pattern in patterns:
                try:
                    import glob
                    for port_name in glob.glob(pattern):
                        if not any(p['port_no'] == port_name for p in self.available_ports):
                             self.available_ports.append({"port_no": port_name, "is_used": False, "device_name": ""})
                except Exception as e: self.logger(f"Error globbing for {pattern} ports: {e}")
        else: self.logger(f"Unsupported platform for port detection: {platform.system()}")
        self.logger(f"Found ports: {[p['port_no'] for p in self.available_ports]}")
        return self.available_ports

    def _assign_port_locally(self, port_name, device_name):
        for port_info in self.available_ports:
            if port_info["port_no"] == port_name:
                port_info["is_used"] = True; port_info["device_name"] = device_name
                self.logger(f"Locally assigned port {port_name} to {device_name}.") # Removed "for testing"
                return True
        return False

    def find_and_assign_sas_port(self):
        self.logger("Attempting to find SAS port...")
        for port_info in [p for p in self.available_ports if not p["is_used"]]:
            port_name = port_info['port_no']
            self.logger(f"Testing port {port_name} for SAS...")
            # Pass the config_manager instance to SASCommunicator
            temp_sas_comm = SASCommunicator(port_name, self.config_manager)
            if temp_sas_comm.open_port(): # open_port sends an initial "80" poll
                time.sleep(0.2) # Increased delay for EGM to respond to the initial poll
                initial_response = temp_sas_comm.receive_data()
                
                sas_confirmed = False
                if initial_response and initial_response.startswith(temp_sas_comm.sas_address):
                    self.logger(f"SAS device responded on {port_name} to initial poll (response: {initial_response})")
                    # Send Get SAS Version for further confirmation
                    temp_sas_comm.get_sas_version_and_serial() # This sends "0154..."
                    time.sleep(0.25) # Allow time for this specific command
                    version_response = temp_sas_comm.receive_data()
                    if version_response and version_response.startswith(temp_sas_comm.sas_address + "54"):
                        self.logger(f"SAS Get Version successful on {port_name}.")
                        sas_confirmed = True
                    else:
                        self.logger(f"SAS Get Version failed or no specific response on {port_name} (got: {version_response}), but initial poll was OK.")
                        sas_confirmed = True # Still consider it SAS if initial poll was fine
                
                temp_sas_comm.close_port() # Close the temporary communicator
                if sas_confirmed:
                    self._assign_port_locally(port_name, "SAS")
                    self.sas_port_name = port_name
                    return port_name
                elif initial_response:
                     self.logger(f"No conclusive SAS confirmation from {port_name}, though initial response was: {initial_response}")
                else:
                    self.logger(f"No initial response from {port_name} for SAS test.")
            else: self.logger(f"Could not open {port_name} for SAS test.")
        self.logger("SAS port not found.")
        return None

    def find_and_assign_card_reader_port(self): # Same as previous version
        reader_type_id = self.config_manager.getint('cardreader', 'type', 2)
        if reader_type_id == 1:
            self.card_reader_port_name = self.config_manager.get('cardreader', 'lib_path', './crt_288B_UR.so')
            self.logger(f"CRT288B card reader: using configured path: {self.card_reader_port_name}")
            return self.card_reader_port_name
        self.logger("Attempting to find serial Card Reader port...")
        for port_info in [p for p in self.available_ports if not p["is_used"]]:
            port_name = port_info['port_no']
            self.logger(f"Testing port {port_name} for Card Reader (type {reader_type_id})...")
            temp_card_reader = CardReaderHandler(port_name, self.config_manager, reader_type_id)
            if temp_card_reader._open_serial_port():
                response = None
                if reader_type_id == 2: # rCloud
                    temp_card_reader._send_rcloud_command("02000235310307")
                    time.sleep(0.1); response = temp_card_reader._receive_rcloud_data()
                    if response and (response.startswith("020003") or response.startswith("020007") or response == "06"):
                        self.logger(f"Card Reader (rCloud) identified on {port_name}")
                        self._assign_port_locally(port_name, "CardReader"); self.card_reader_port_name = port_name
                        temp_card_reader._close_serial_port(); return port_name
                temp_card_reader._close_serial_port()
                if response: self.logger(f"No conclusive CR response from {port_name}, got: {response}")
            else: self.logger(f"Could not open {port_name} for CR test.")
        self.logger("Serial Card Reader port not found."); return None

    def find_and_assign_bill_acceptor_port(self): # Same as previous version
        acceptor_type_id = self.config_manager.getint('billacceptor', 'typeid', 0)
        if acceptor_type_id == 0: self.logger("BA is SAS controlled."); return None
        self.logger("Attempting to find direct serial Bill Acceptor port...")
        for port_info in [p for p in self.available_ports if not p["is_used"]]:
            port_name = port_info['port_no']
            self.logger(f"Testing port {port_name} for BA (type {acceptor_type_id})...")
            temp_ba_handler = BillAcceptorHandler(port_name, self.config_manager, acceptor_type_id)
            if temp_ba_handler._open_direct_port():
                temp_ba_handler.request_status(); time.sleep(0.2)
                response = temp_ba_handler._receive_direct_data(); temp_ba_handler._close_direct_port()
                if response:
                    self.logger(f"BA (type {acceptor_type_id}) identified on {port_name}")
                    self._assign_port_locally(port_name, "BillAcceptor"); self.bill_acceptor_port_name = port_name
                    return port_name
            else: self.logger(f"Could not open {port_name} for BA test.")
        self.logger("Direct serial Bill Acceptor port not found."); return None

class SASCommunicator:
    def __init__(self, port_name, config_manager_instance, baud_rate=19200, timeout=0.1):
        self.port_name = port_name; self.baud_rate = baud_rate; self.timeout = timeout
        self.config_manager = config_manager_instance; self.serial_port = None
        self.sas_address = self.config_manager.get('sas', 'address', '01') # EGM's SAS Address
        self.last_sent_poll_type = 81; self.is_port_open = False # Start with 81 so first poll is 80
        self.logger = self.config_manager.logger
        self.use_termios_for_parity = platform.system() == "Linux" and \
                                      self.config_manager.getint('machine', 'devicetypeid', 8) not in [1, 4, 11]
        if self.use_termios_for_parity:
            try:
                import termios; self.termios = termios
                self.CMSPAR = getattr(termios, 'CMSPAR', 0o10000000000) # Octal for PAREXT
                if self.CMSPAR == 0o10000000000 and not hasattr(termios, 'CMSPAR'):
                     self.logger("termios.CMSPAR not found, using fallback 0o10000000000.")
            except ImportError: self.logger("Warning: termios module not found."); self.use_termios_for_parity = False
            except AttributeError: self.logger("Warning: termios attributes (CMSPAR/PARENB/PARODD) missing."); self.use_termios_for_parity = False
    
    def open_port(self):
        if self.is_port_open: self.logger(f"SAS port {self.port_name} already open."); return True
        try:
            self.serial_port = serial.Serial()
            self.serial_port.port = self.port_name; self.serial_port.baudrate = self.baud_rate
            self.serial_port.timeout = self.timeout; self.serial_port.parity = serial.PARITY_NONE
            self.serial_port.stopbits = serial.STOPBITS_ONE; self.serial_port.bytesize = serial.EIGHTBITS
            self.serial_port.xonxoff = False; self.serial_port.dtr = True; self.serial_port.rts = False
            self.serial_port.open(); self.is_port_open = True
            self.logger(f"SAS port {self.port_name} opened with PARITY_NONE.")
            
            device_type_id = self.config_manager.getint('machine', 'devicetypeid', 8)
            if device_type_id in [1, 4]: # Novomatic/Octavian
                self.logger("Novomatic/Octavian: initial polls with NONE parity, then switch to EVEN.")
                self._send_raw_command_platform_specific("80", is_poll=True); time.sleep(0.05)
                self._send_raw_command_platform_specific("81", is_poll=True); time.sleep(0.05)
                self.serial_port.close(); self.serial_port.parity = serial.PARITY_EVEN; self.serial_port.open()
                self.logger(f"SAS port {self.port_name} re-opened with PARITY_EVEN.")
            else: # Initial poll for other devices
                self._send_raw_command_platform_specific("80", is_poll=True) # Send initial poll
                time.sleep(0.05) # Give EGM time to wake up
            return True
        except serial.SerialException as e: self.logger(f"Error opening SAS port {self.port_name}: {e}"); self.is_port_open = False; return False
        except Exception as e: self.logger(f"Unexpected error opening SAS port {self.port_name}: {e}"); self.is_port_open = False; return False

    def close_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close(); self.is_port_open = False
            self.logger(f"SAS port {self.port_name} closed.")

    def _send_raw_command_platform_specific(self, command_hex_full, is_poll=False):
        """ Sends a command hex string. `command_hex_full` is the exact byte(s) to send. """
        if not self.is_port_open or not self.serial_port: self.logger("SAS port not open."); return
        data_bytes = decode_to_hex(command_hex_full)
        
        # Device types 1 (Novomatic) and 4 (Octavian) use PARITY_EVEN (handled by open_port)
        # Device type 11 (Interblock) and Windows use PARITY_NONE (default)
        # Other Linux devices use Mark/Space via termios
        device_type_id = self.config_manager.getint('machine', 'devicetypeid', 8)
        
        if self.use_termios_for_parity and device_type_id not in [1, 4, 11]:
            try:
                fd = self.serial_port.fileno()
                iflag, oflag, cflag, lflag, ispeed, ospeed, cc = self.termios.tcgetattr(fd)
                original_cflag = cflag
                
                # First byte (address for commands, or the poll byte itself) with MARK parity
                cflag_mark = (original_cflag | self.termios.PARENB | self.CMSPAR | self.termios.PARODD)
                # Ensure CSTOPB is NOT set for 1 stop bit, which is typical for Mark/Space
                cflag_mark &= ~self.termios.CSTOPB 
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, [iflag, oflag, cflag_mark, lflag, ispeed, ospeed, cc])
                self.serial_port.write(data_bytes[0:1]); self.serial_port.flush()
                
                if len(data_bytes) > 1: # If there are more bytes
                    time.sleep(0.001) # Small delay as in original code (saswaittime)
                    # Subsequent bytes with SPACE parity
                    cflag_space = (original_cflag | self.termios.PARENB | self.CMSPAR) & ~self.termios.PARODD
                    cflag_space &= ~self.termios.CSTOPB
                    self.termios.tcsetattr(fd, self.termios.TCSADRAIN, [iflag, oflag, cflag_space, lflag, ispeed, ospeed, cc])
                    self.serial_port.write(data_bytes[1:]); self.serial_port.flush()
                
                # Restore original cflag (which should be PARITY_NONE settings)
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, [iflag, oflag, original_cflag, lflag, ispeed, ospeed, cc])
            except Exception as e: 
                self.logger(f"Error setting termios parity: {e}. Sending with current port settings.")
                self.serial_port.write(data_bytes) # Fallback
        else: # For Windows, Novomatic, Octavian, Interblock (uses port's current parity)
            self.serial_port.write(data_bytes)
        
        # self.serial_port.flushInput() # Optional: Clear input buffer after sending

    def send_general_poll(self):
        if not self.is_port_open: return
        # Poll byte is determined, e.g., "80" or "81" (machine address 0 + poll)
        # The EGM at self.sas_address is expected to respond if this poll targets it.
        # Original script just sent "80" or "81". Let's assume EGM is address 01 for now for clarity.
        # If EGM is address 01, it responds to poll "81" (01 | 80).
        # If EGM is address 00 (less common for slots), it responds to "80".
        # The key is that the HOST sends "80" or "81", not "0180" or "0181".
        poll_byte_to_send = "81" if self.last_sent_poll_type == 80 else "80"
        
        self.logger(f"TX Poll Byte: {poll_byte_to_send}")
        self._send_raw_command_platform_specific(poll_byte_to_send, is_poll=True)
        self.last_sent_poll_type = int(poll_byte_to_send, 16)


    def send_command(self, command_name, command_body_hex_no_addr, add_address_and_crc=True):
        """
        command_body_hex_no_addr: e.g., "54" for GetVersion, or "72<len><payload>" for AFT.
        """
        if not self.is_port_open: self.logger(f"Cannot send '{command_name}', port not open."); return
        
        full_command_hex = command_body_hex_no_addr
        if add_address_and_crc:
            # Prepend the EGM's SAS address
            command_with_addr = self.sas_address + command_body_hex_no_addr
            full_command_hex = get_crc(command_with_addr) # CRC is calculated on (Address + Body)
        
        self.logger(f"TX SAS ('{command_name}'): {full_command_hex}")
        self._send_raw_command_platform_specific(full_command_hex, is_poll=False)
        
    def receive_data(self, timeout_override=None):
        if not self.is_port_open or not self.serial_port: self.logger("SAS port not open."); return None
        original_timeout = self.serial_port.timeout
        if timeout_override is not None: self.serial_port.timeout = timeout_override
        buffer = bytearray()
        try:
            # Read initial byte(s)
            initial_data = self.serial_port.read(self.serial_port.in_waiting or 1)
            if initial_data:
                buffer.extend(initial_data)
                # Poll for more data with short inter-byte delays
                # SAS messages are typically short, but this handles potential fragmentation
                for _ in range(5): # Try a few times to catch trailing bytes
                    time.sleep(0.005) # Inter-byte delay from original script
                    if self.serial_port.in_waiting > 0:
                        buffer.extend(self.serial_port.read(self.serial_port.in_waiting))
                    else:
                        break 
        except Exception as e: self.logger(f"Error receiving SAS data: {e}")
        finally:
            if timeout_override is not None: self.serial_port.timeout = original_timeout
        hex_data = buffer.hex().upper()
        if hex_data: self.logger(f"RX SAS: {hex_data}")
        return hex_data if hex_data else None

    def _parse_sas_message(self, message_hex): # Same as previous version
        if not message_hex or len(message_hex) < 2: return None
        parsed_data = {"raw": message_hex, "type": "unknown", "address_match": False}
        received_address = message_hex[0:2]
        # Important: A response from EGM will start with *its own address* (self.sas_address)
        if received_address == self.sas_address:
            parsed_data["address_match"] = True
            command_byte = message_hex[2:4] if len(message_hex) >= 4 else None
            parsed_data["command_byte"] = command_byte # This is the command byte *in the EGM's response*
            if command_byte == "72": parsed_data["type"] = "AFT_RESPONSE"; parsed_data["transfer_status"] = message_hex[8:10] if len(message_hex) >= 10 else None
            elif command_byte == "74": parsed_data["type"] = "BALANCE_INFO"; parsed_data["asset_number_resp"] = message_hex[6:14] if len(message_hex) >= 14 else None; parsed_data["game_lock_status"] = message_hex[14:16] if len(message_hex) >= 16 else None
            elif command_byte == "54": parsed_data["type"] = "SAS_VERSION_INFO"; parsed_data["sas_version"] = hex_to_int(message_hex[8:14]) if len(message_hex) >= 14 else None # Example parsing
            elif command_byte == "73" and len(message_hex) >= 16: parsed_data["type"] = "ASSET_INFO_RESPONSE"; parsed_data["registration_status"] = message_hex[6:8]; parsed_data["asset_number_hex_reversed"] = message_hex[8:16]
            elif command_byte == "FF": # General Exception from EGM
                 parsed_data["type"] = "GENERAL_EXCEPTION_FROM_EGM" # To distinguish from host-side FF
                 if len(message_hex) >= 6: parsed_data["exception_code"] = message_hex[4:6] # The actual exception code
        elif len(message_hex) == 2 and (message_hex == "80" or message_hex == "81"): # This should not happen as EGM response
            parsed_data["type"] = "UNEXPECTED_POLL_BYTE_AS_RESPONSE"
        elif message_hex.startswith("FF"): # A general exception not tied to our address - could be noise or other device
            parsed_data["type"] = "GENERAL_EXCEPTION_UNKNOWN_SOURCE"
            if len(message_hex) >= 4: parsed_data["exception_code"] = message_hex[2:4]

        return parsed_data

    def process_received_message(self, message_hex): # Same as previous
        if not message_hex: return None
        parsed_message = self._parse_sas_message(message_hex)
        if parsed_message and parsed_message["address_match"]:
            self.logger(f"Processed SAS Message: {parsed_message}")
        elif parsed_message:
             self.logger(f"Ignored SAS Message (no address match or unhandled): {parsed_message}")
             return None
        return parsed_message

    def request_balance_info(self, lock_request_code="FF", for_info=True):
        lock_timeout_bcd = "0000"
        if lock_request_code != "FF" and lock_request_code != "00": lock_timeout_bcd = "9000"
        self.send_command("RequestBalanceInfo", f"74{lock_request_code}{lock_timeout_bcd}")

    def cancel_aft_lock(self): self.send_command("CancelAFTLock", "7480030000")
    def get_sas_version_and_serial(self): self.send_command("GetSASVersion", "54")
    def get_asset_number_info(self): self.send_command("ReadAssetNumber", "7301FF")

class AssetManager: # No changes
    def __init__(self, sas_communicator, config_manager_instance):
        self.sas_comm = sas_communicator; self.config_manager = config_manager_instance
        self.current_asset_number_int = 0
        self.current_asset_number_hex_reversed = self.config_manager.get('sas', 'assetnumber', '00000000')
        self.registration_key = self.config_manager.get('sas', 'registrationkey', '0000000000000000000000000000000000000000')
        self.logger = self.config_manager.logger
        if self.current_asset_number_hex_reversed and self.current_asset_number_hex_reversed != '00000000':
            self.current_asset_number_int = self._read_asset_to_int(self.current_asset_number_hex_reversed)
    def _get_asset_binary(self, asset_int):
        hex_str = hex(int(asset_int)).split('x')[-1].upper().zfill(8)
        return "".join(reversed([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])).ljust(8, '0')[:8]
    def _read_asset_to_int(self, rev_hex_8_chars):
        if len(rev_hex_8_chars) != 8: self.logger(f"Warn: Asset hex '{rev_hex_8_chars}' not 8 chars."); return 0
        norm_hex = "".join(reversed([rev_hex_8_chars[i:i+2] for i in range(0, len(rev_hex_8_chars), 2)]))
        try: return int(norm_hex, 16)
        except ValueError: self.logger(f"Error converting asset hex '{norm_hex}' to int."); return 0
    def update_asset_info_from_sas_response(self, parsed_sas_message):
        if not parsed_sas_message: return
        asset_hex_from_resp = None
        if parsed_sas_message.get("type") == "ASSET_INFO_RESPONSE": asset_hex_from_resp = parsed_sas_message.get("asset_number_hex_reversed")
        elif parsed_sas_message.get("type") == "BALANCE_INFO": asset_hex_from_resp = parsed_sas_message.get("asset_number_resp")
        if asset_hex_from_resp and len(asset_hex_from_resp) == 8:
            new_asset_int = self._read_asset_to_int(asset_hex_from_resp)
            if new_asset_int != 0 and new_asset_int != self.current_asset_number_int :
                self.logger(f"Asset number updated from SAS: {new_asset_int} (Hex: {asset_hex_from_resp})")
                self.current_asset_number_int = new_asset_int; self.current_asset_number_hex_reversed = asset_hex_from_resp
                self.config_manager.set_value('sas', 'assetnumber', self.current_asset_number_hex_reversed)
            elif new_asset_int == 0 and asset_hex_from_resp != "00000000": self.logger(f"Warn: Read asset {asset_hex_from_resp} converted to 0.")
    def read_asset_from_machine(self): self.logger("Requesting asset number..."); self.sas_comm.get_asset_number_info()
    def register_asset_on_machine(self, asset_num_to_reg_int=None, mode="register"):
        asset_int = asset_num_to_reg_int if asset_num_to_reg_int is not None else self.current_asset_number_int
        asset_hex = self.current_asset_number_hex_reversed
        if asset_int != 0: asset_hex = self._get_asset_binary(asset_int)
        elif self.current_asset_number_int == 0 and self.current_asset_number_hex_reversed == '00000000': self.logger("Asset 0 not configured.")
        reg_mode = "00" if mode == "register" else "01"; pos_id = "00000000"
        # Command 73 payload starts after address and command byte (73) and length (1D)
        # So, command_body_hex_no_addr should be "1D" + mode + asset_hex + reg_key + pos_id
        cmd_payload = f"1D{reg_mode}{asset_hex}{self.registration_key}{pos_id}"
        self.logger(f"Registering asset: {asset_int} (Hex: {asset_hex}), Mode: {mode}")
        self.sas_comm.send_command("RegisterAssetNumber", "73" + cmd_payload, add_address_and_crc=True)


class AFTHandler: # No changes
    def __init__(self, sas_communicator, config_manager_instance, asset_manager):
        self.sas_comm = sas_communicator; self.config_manager = config_manager_instance; self.asset_manager = asset_manager
        self.is_transfer_in_progress = False; self.last_transfer_status = None
        self.current_transaction_id = int(self.config_manager.get('payment', 'transactionid', 0))
        self.logger = self.config_manager.logger
    def _get_next_transaction_id(self, increment=True):
        if increment: self.current_transaction_id = (self.current_transaction_id % 255)+1; self.config_manager.set_value('payment', 'transactionid', self.current_transaction_id)
        return self.current_transaction_id
    def _format_amount_bcd(self, amount_decimal, num_bytes=5): return add_left_bcd(str(int(amount_decimal*100)), num_bytes)
    def _construct_aft_payload(self, transfer_type_byte, cash_amt, rest_amt, non_rest_amt, pool_id_hex):
        tx_id = self._get_next_transaction_id(); tx_id_hex = "".join(f"{ord(c):02x}" for c in str(tx_id)); tx_id_len_hex = f"{int(len(tx_id_hex)/2):02x}".zfill(2)
        asset_num_hex = self.asset_manager.current_asset_number_hex_reversed; reg_key_hex = self.asset_manager.registration_key
        payload = "0000" + transfer_type_byte + self._format_amount_bcd(cash_amt, 5) + self._format_amount_bcd(rest_amt, 5) + self._format_amount_bcd(non_rest_amt, 5)
        transfer_flags = "07"; 
        if self.config_manager.getint('machine', 'config_is_cashout_soft', 0) == 1: transfer_flags = "03"
        if transfer_type_byte == "0B": transfer_flags = "0B" # Handpay
        payload += transfer_flags + asset_num_hex + reg_key_hex + tx_id_len_hex + tx_id_hex + "00000000" + pool_id_hex + "00"
        return payload, tx_id
    def transfer_to_machine(self, cash_amt, rest_amt, non_rest_amt, transfer_type="00", pool_id="0000"):
        if self.is_transfer_in_progress: self.logger("AFT Error: Transfer in progress."); return False
        self.is_transfer_in_progress = True; self.last_transfer_status = "PENDING_TO_MACHINE"
        payload, tx_id = self._construct_aft_payload(transfer_type, cash_amt, rest_amt, non_rest_amt, pool_id)
        cmd_len_hex = f"{int(len(payload)/2):02x}".zfill(2); cmd_body_no_addr = f"72{cmd_len_hex}{payload}"
        self.sas_comm.send_command("AFT_TransferToMachine", cmd_body_no_addr, add_address_and_crc=True)
        self.logger(f"AFT to machine: TxID {tx_id}, C {cash_amt}, R {rest_amt}, NR {non_rest_amt}"); return True
    def transfer_from_machine(self, cash_amt, rest_amt, non_rest_amt, transfer_type="80", pool_id="0000"):
        if self.is_transfer_in_progress: self.logger("AFT Error: Transfer in progress."); return False
        self.is_transfer_in_progress = True; self.last_transfer_status = "PENDING_FROM_MACHINE"
        payload, tx_id = self._construct_aft_payload(transfer_type, cash_amt, rest_amt, non_rest_amt, pool_id)
        cmd_len_hex = f"{int(len(payload)/2):02x}".zfill(2); cmd_body_no_addr = f"72{cmd_len_hex}{payload}"
        self.sas_comm.send_command("AFT_TransferFromMachine", cmd_body_no_addr, add_address_and_crc=True)
        self.logger(f"AFT from machine: TxID {tx_id}, ExpC {cash_amt}, ExpR {rest_amt}"); return True
    def update_transfer_status(self, sas_parsed_response):
        if sas_parsed_response and sas_parsed_response.get("type") == "AFT_RESPONSE":
            status_code = sas_parsed_response.get("transfer_status"); self.last_transfer_status = status_code
            if status_code == "00": self.logger("AFT successful."); self.is_transfer_in_progress = False
            elif status_code == "40": self.logger("AFT pending...")
            else: self.logger(f"AFT status: {status_code}"); self.is_transfer_in_progress = False

class BillAcceptorHandler: # No changes
    def __init__(self, port_name_or_sas_comm, config_manager_instance, acceptor_type_id):
        self.config_manager = config_manager_instance; self.acceptor_type_id = acceptor_type_id
        self.port_name = None; self.serial_port = None; self.sas_communicator = None
        self.is_enabled_hw = False; self.is_enabled_sas = False; self.mei_last_ack_nack = "10"; self.last_bill_escrowed = None
        self.logger = self.config_manager.logger
        if self.acceptor_type_id == 0:
            if not isinstance(port_name_or_sas_comm, SASCommunicator): raise ValueError("SASComm for SAS BA.")
            self.sas_communicator = port_name_or_sas_comm; self.logger("BA: SAS controlled.")
        else:
            self.port_name = port_name_or_sas_comm; self.baudrate = 9600; self.parity = serial.PARITY_EVEN
            self.bytesize = serial.SEVENBITS if acceptor_type_id == 2 else serial.EIGHTBITS
            self.logger(f"BA: Direct serial {self.port_name}, type {acceptor_type_id}")
    def _open_direct_port(self):
        if self.acceptor_type_id == 0 or not self.port_name: return True
        if self.serial_port and self.serial_port.is_open: return True
        try:
            self.serial_port = serial.Serial(port=self.port_name, baudrate=self.baudrate, parity=self.parity,
                                             bytesize=self.bytesize, stopbits=serial.STOPBITS_ONE, timeout=0.1)
            self.logger(f"BA port {self.port_name} opened."); return True
        except serial.SerialException as e: self.logger(f"Error opening BA port {self.port_name}: {e}"); return False
    def _close_direct_port(self):
        if self.serial_port and self.serial_port.is_open: self.serial_port.close(); self.logger(f"BA port {self.port_name} closed.")
    def _send_direct_command(self, cmd_hex):
        if self.acceptor_type_id == 0 or not self.serial_port or not self.serial_port.is_open: self.logger("BA: No direct send."); return
        try: self.serial_port.write(decode_to_hex(cmd_hex))
        except Exception as e: self.logger(f"Error sending direct BA cmd: {e}")
    def _receive_direct_data(self, num_bytes=None):
        if self.acceptor_type_id == 0 or not self.serial_port or not self.serial_port.is_open: return None
        try:
            data = self.serial_port.read(self.serial_port.in_waiting or 1) if not num_bytes else self.serial_port.read(num_bytes)
            return data.hex().upper() if data else None
        except Exception as e: self.logger(f"Error receiving direct BA data: {e}"); return None
    def _get_mei_ack(self): self.mei_last_ack_nack = "11" if self.mei_last_ack_nack == "10" else "10"; return self.mei_last_ack_nack
    def _get_mei_msg_crc(self, cmd_body_no_crc):
        temp_cmd = cmd_body_no_crc.replace(" ", "") + "00"; hex_data = decode_to_hex(temp_cmd); bcc = 0
        for i in range(1, len(hex_data) - 1): bcc ^= hex_data[i]
        return cmd_body_no_crc.replace(" ", "") + f"{bcc:02X}"
    def enable(self):
        if self.acceptor_type_id == 0: self.sas_communicator.send_command("EnableBASAS", "06"); self.is_enabled_sas = True
        elif self.acceptor_type_id == 1: self._send_direct_command("FC06C30004D6"); self.is_enabled_hw = True
        elif self.acceptor_type_id == 2: cmd = self._get_mei_msg_crc(f"0208{self._get_mei_ack()}7F1C1003"); self._send_direct_command(cmd); self.is_enabled_hw = True
        self.logger("BA enabled.")
    def disable(self):
        if self.acceptor_type_id == 0: self.sas_communicator.send_command("DisableBASAS", "07"); self.is_enabled_sas = False
        elif self.acceptor_type_id == 1: self._send_direct_command("FC06C3018DC7"); self.is_enabled_hw = False
        elif self.acceptor_type_id == 2: cmd = self._get_mei_msg_crc(f"0208{self._get_mei_ack()}001C1003"); self._send_direct_command(cmd); self.is_enabled_hw = False
        self.logger("BA disabled.")
    def request_status(self):
        if self.acceptor_type_id == 1: self._send_direct_command("FC05112756")
        elif self.acceptor_type_id == 2:
            ack = self._get_mei_ack(); cmd_body = f"0208{ack}7F1C1003" if self.is_enabled_hw else f"0208{ack}001C1003"
            self._send_direct_command(self._get_mei_msg_crc(cmd_body))
    def poll_events(self):
        if self.acceptor_type_id == 0: return None
        raw_data = self._receive_direct_data()
        if not raw_data: return None
        if self.acceptor_type_id == 2 and raw_data.startswith("02"): self.logger(f"MEI Data: {raw_data} - Needs parsing")
        return {"event_type": "BILL_STATUS", "data": raw_data, "port": self.port_name}

class CardReaderHandler: # No changes
    def __init__(self, port_name_or_lib_path, config_manager_instance, reader_type_id):
        self.config_manager = config_manager_instance; self.reader_type_id = reader_type_id
        self.port_name = None; self.serial_port = None; self.crt_lib = None
        self.is_card_present = False; self.current_card_uid = None; self.last_card_status_crt288b = 0
        self.logger = self.config_manager.logger
        if self.reader_type_id == 1: self.lib_path = port_name_or_lib_path; self._init_crt288b()
        else: self.port_name = port_name_or_lib_path; self.baudrate = 9600
    def _init_crt288b(self):
        if platform.system().startswith("Window"): self.logger("CRT288B .so lib not for Windows."); return
        try: self.crt_lib = ctypes.CDLL(self.lib_path); self.logger(f"CRT288B lib loaded: {self.lib_path}")
        except Exception as e: self.logger(f"Error loading CRT288B lib: {e}"); self.crt_lib = None
    def _open_serial_port(self):
        if self.reader_type_id == 1 or not self.port_name: return True
        if self.serial_port and self.serial_port.is_open: return True
        try:
            self.serial_port = serial.Serial(port=self.port_name, baudrate=self.baudrate, timeout=0.1)
            if self.reader_type_id == 2: self.serial_port.bytesize=serial.EIGHTBITS; self.serial_port.parity=serial.PARITY_NONE; self.serial_port.stopbits=serial.STOPBITS_ONE
            self.logger(f"CR port {self.port_name} opened."); return True
        except serial.SerialException as e: self.logger(f"Error opening CR port {self.port_name}: {e}"); return False
    def _close_serial_port(self):
        if self.serial_port and self.serial_port.is_open: self.serial_port.close(); self.logger(f"CR port {self.port_name} closed.")
    def _send_rcloud_command(self, cmd_hex):
        if not self.serial_port or not self.serial_port.is_open: return
        try: self.serial_port.write(decode_to_hex(cmd_hex))
        except Exception as e: self.logger(f"Error sending rCloud cmd: {e}")
    def _receive_rcloud_data(self):
        if not self.serial_port or not self.serial_port.is_open: return None
        buffer = bytearray()
        try:
            if self.serial_port.in_waiting > 0: buffer.extend(self.serial_port.read(self.serial_port.in_waiting))
            return buffer.hex().upper() if buffer else None
        except Exception as e: self.logger(f"Error receiving rCloud data: {e}"); return None
    def check_for_card(self):
        uid, present = None, False
        if self.reader_type_id == 1:
            if not self.crt_lib: return "ERROR", None
            try:
                arr=(ctypes.c_ubyte*1024)(); open_res=self.crt_lib.CRT288B_OpenDev(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(0))
                if open_res == -5: self.last_card_status_crt288b = -5; return "ERROR", None
                self.last_card_status_crt288b=open_res; res=self.crt_lib.CRT288B_GetCardUID(arr); self.crt_lib.CRT288B_CloseDev()
                if res > 0: raw=bytearray(arr[:res]).hex().upper(); uid=raw[6:14] if raw.startswith("590400") and len(raw)>=14 else (raw if len(raw)==8 else None); present=bool(uid)
            except Exception as e: self.logger(f"Error CRT288B: {e}"); return "ERROR", None
        elif self.reader_type_id == 2:
            self._send_rcloud_command("02000235310307"); time.sleep(0.05); resp=self._receive_rcloud_data()
            if resp and resp.startswith("0200073531") and len(resp) >= 22:
                uid_start = resp.find("3531")+4
                if uid_start!=3 and len(resp) >= uid_start+8: uid=resp[uid_start:uid_start+8]; present=True
            elif resp and resp.startswith("0200033531"): present=False
        if present and not self.is_card_present: self.is_card_present=True; self.current_card_uid=uid; return "CARD_INSERTED", uid
        elif not present and self.is_card_present: old_uid=self.current_card_uid; self.is_card_present=False; self.current_card_uid=None; return "CARD_REMOVED", old_uid
        if present and self.is_card_present and self.current_card_uid != uid: old_uid=self.current_card_uid; self.current_card_uid=uid; return "CARD_SWAPPED", (old_uid, uid)
        return "NO_CHANGE", self.current_card_uid

class SlotMachineApplication: # No changes
    def __init__(self, config_file_path="settings.ini"):
        self.config_file_path = config_file_path; self.config = None; self.port_mgr = None
        self.sas_comm = None; self.asset_mgr = None; self.aft_handler = None
        self.bill_acceptor_handler = None; self.card_reader_handler = None
        self.running = False; self.sas_poll_timer = None; self.card_read_timer = None; self.bill_acceptor_poll_timer = None
        self.logger = print
    def _delete_config_file(self):
        if os.path.exists(self.config_file_path):
            try: os.remove(self.config_file_path); self.logger(f"Removed config: {self.config_file_path}")
            except OSError as e: self.logger(f"Error removing config {self.config_file_path}: {e}")
    def _setup_configuration_and_ports(self):
        self._delete_config_file(); self.config = ConfigManager(self.config_file_path); self.logger = self.config.logger
        self.port_mgr = PortManager(self.config); self.port_mgr.find_available_serial_ports()
        self.port_mgr.find_and_assign_sas_port(); self.port_mgr.find_and_assign_card_reader_port(); self.port_mgr.find_and_assign_bill_acceptor_port()
        self.config.set_value('sas', 'port', self.port_mgr.sas_port_name)
        self.config.set_value('cardreader', 'port_or_path', self.port_mgr.card_reader_port_name)
        self.config.set_value('billacceptor', 'port', self.port_mgr.bill_acceptor_port_name)
        self.config.apply_operational_defaults(); self.config.save()
        self.logger("Initial config and port detection complete.")
    def initialize_components(self):
        self.logger("Initializing components based on detected/configured ports...")
        if self.port_mgr.sas_port_name:
            self.sas_comm = SASCommunicator(self.port_mgr.sas_port_name, self.config)
            if self.sas_comm.open_port():
                self.asset_mgr = AssetManager(self.sas_comm, self.config); self.aft_handler = AFTHandler(self.sas_comm, self.config, self.asset_mgr)
            else: self.logger(f"Failed to open SAS port {self.port_mgr.sas_port_name}"); self.sas_comm = None
        else: self.logger("SAS port was not assigned.")
        if self.port_mgr.card_reader_port_name:
            reader_type = self.config.getint('cardreader', 'type', 2)
            self.card_reader_handler = CardReaderHandler(self.port_mgr.card_reader_port_name, self.config, reader_type)
            if reader_type != 1 and not self.card_reader_handler._open_serial_port():
                self.logger(f"Failed to open CR port {self.port_mgr.card_reader_port_name}"); self.card_reader_handler = None
        else: self.logger("CR port/path was not assigned.")
        ba_type = self.config.getint('billacceptor', 'typeid', 0)
        if ba_type != 0:
            if self.port_mgr.bill_acceptor_port_name:
                self.bill_acceptor_handler = BillAcceptorHandler(self.port_mgr.bill_acceptor_port_name, self.config, ba_type)
                if not self.bill_acceptor_handler._open_direct_port(): self.logger(f"Failed to open BA port {self.port_mgr.bill_acceptor_port_name}"); self.bill_acceptor_handler = None
            else: self.logger("Direct serial BA port not assigned.")
        elif self.sas_comm: self.bill_acceptor_handler = BillAcceptorHandler(self.sas_comm, self.config, 0)
        else: self.logger("BA SAS controlled, but SAS comm unavailable.")
        self.logger("Component initialization finished.")
    def _sas_polling_loop(self):
        if not self.running or not self.sas_comm or not self.sas_comm.is_port_open: return
        self.sas_comm.send_general_poll(); response_hex = self.sas_comm.receive_data(timeout_override=0.05)
        if response_hex:
            parsed_msg = self.sas_comm.process_received_message(response_hex)
            if parsed_msg and self.asset_mgr: self.asset_mgr.update_asset_info_from_sas_response(parsed_msg)
        if self.running: self.sas_poll_timer = threading.Timer(0.04, self._sas_polling_loop); self.sas_poll_timer.daemon=True; self.sas_poll_timer.start()
    def _card_reader_loop(self):
        if not self.running or not self.card_reader_handler: return
        event, uid_data = self.card_reader_handler.check_for_card()
        if event=="CARD_INSERTED": self.logger(f"MainApp: Card Inserted - UID: {uid_data}")
        elif event=="CARD_REMOVED": self.logger(f"MainApp: Card Removed - UID: {uid_data}")
        elif event=="ERROR": self.logger("MainApp: Card Reader Error")
        if self.running:
            interval = 0.5; 
            if self.card_reader_handler.reader_type_id == 2: interval = 0.1 # Faster for rCloud
            self.card_read_timer = threading.Timer(interval, self._card_reader_loop); self.card_read_timer.daemon=True; self.card_read_timer.start()
    def _bill_acceptor_loop(self):
        if not self.running or not self.bill_acceptor_handler or self.bill_acceptor_handler.acceptor_type_id == 0: return
        self.bill_acceptor_handler.request_status(); time.sleep(0.05)
        event_data = self.bill_acceptor_handler.poll_events()
        if event_data: self.logger(f"MainApp: BA Event - {event_data}")
        if self.running: self.bill_acceptor_poll_timer = threading.Timer(0.2, self._bill_acceptor_loop); self.bill_acceptor_poll_timer.daemon=True; self.bill_acceptor_poll_timer.start()
    def start(self):
        self._setup_configuration_and_ports(); self.initialize_components(); self.running = True
        if self.sas_comm and self.sas_comm.is_port_open: self._sas_polling_loop()
        if self.card_reader_handler:
            if self.card_reader_handler.reader_type_id != 1 and (not self.card_reader_handler.serial_port or not self.card_reader_handler.serial_port.is_open): self.card_reader_handler._open_serial_port()
            if (self.card_reader_handler.reader_type_id == 1 and self.card_reader_handler.crt_lib) or \
               (self.card_reader_handler.reader_type_id != 1 and self.card_reader_handler.serial_port and self.card_reader_handler.serial_port.is_open): self._card_reader_loop()
        if self.bill_acceptor_handler and self.bill_acceptor_handler.acceptor_type_id != 0:
            if not self.bill_acceptor_handler.serial_port or not self.bill_acceptor_handler.serial_port.is_open: self.bill_acceptor_handler._open_direct_port()
            if self.bill_acceptor_handler.serial_port and self.bill_acceptor_handler.serial_port.is_open: self._bill_acceptor_loop()
        self.logger("Slot Machine App Started. Ctrl+C to exit.")
        try:
            while self.running: time.sleep(1) 
        except KeyboardInterrupt: self.logger("Shutdown requested.")
        finally: self.shutdown()
    def shutdown(self):
        self.logger("Shutting down..."); self.running = False
        if self.sas_poll_timer: self.sas_poll_timer.cancel()
        if self.card_read_timer: self.card_read_timer.cancel()
        if self.bill_acceptor_poll_timer: self.bill_acceptor_poll_timer.cancel()
        if self.sas_comm: self.sas_comm.close_port()
        if self.card_reader_handler and self.card_reader_handler.reader_type_id != 1: self.card_reader_handler._close_serial_port()
        if self.bill_acceptor_handler and self.bill_acceptor_handler.acceptor_type_id != 0: self.bill_acceptor_handler._close_direct_port()
        if self.config: self.config.save()
        self.logger("Shutdown complete.")

if __name__ == "__main__":
    app = SlotMachineApplication(config_file_path="settings.ini")
    app.start()
