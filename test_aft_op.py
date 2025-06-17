#!/usr/bin/env python3
"""
AFT Add Credit Test Application - CORRECTED
Based on the original SAS communication logic from raspberryPython_orj.py.
For testing AFT operations on Raspberry Pi

Usage: python3 test_aft_op.py <amount> [port]
Examples: 
    python3 test_aft_op.py 100.50
    python3 test_aft_op.py 50 /dev/ttyUSB0
    python3 test_aft_op.py 25 /dev/ttyUSB1
"""

import serial
import serial.tools.list_ports
import sys
import datetime
import time
import threading
import platform
from decimal import Decimal
from crccheck.crc import CrcKermit

# Import termios for correct parity switching on Linux
if platform.system() != "Windows":
    import termios

# --- Configuration ---
# This will be automatically detected, but you can hardcode it for testing.
SAS_PORT = None
SAS_BAUDRATE = 19200
SAS_ADDRESS = "01"
ASSET_NUMBER = "6C000000"  # Asset 108 (0x6C) in little-endian hex, 4 bytes
REGISTRATION_KEY = "0000000000000000000000000000000000000000"  # 20 bytes of zeros
DEVICE_TYPE_ID = 8  # CRITICAL: Main app detected device type 8, not 3!

# --- Global Variables ---
sasport = None
transaction_id_counter = int(datetime.datetime.now().timestamp()) % 10000
polling_active = False
aft_response_received = False
aft_transfer_status = None
balance_response_received = False
balance_amount = Decimal('0.0')

# --- Utility Functions (from original app) ---

def AddLeftString(text, char_to_add, total_length):
    """Pads a string on the left."""
    while len(text) < total_length:
        text = char_to_add + text
    return text

def AddLeftBCD(number, length_in_bytes):
    """Encodes a number into BCD format with specified byte length."""
    try:
        number_str = str(int(number))
        if len(number_str) % 2 != 0:
            number_str = "0" + number_str
        
        hex_str = ""
        for i in range(0, len(number_str), 2):
            hex_str += f"{int(number_str[i]):X}{int(number_str[i+1]):X}"

        # Pad with leading zeros to meet the required byte length
        while len(hex_str) < length_in_bytes * 2:
            hex_str = "00" + hex_str
        return hex_str
    except ValueError:
        return "00" * length_in_bytes


def GetCRC(command_hex):
    """Calculates the 16-bit Kermit CRC and appends it in the correct (reversed) order for SAS."""
    try:
        data = bytearray.fromhex(command_hex)
        crc_instance = CrcKermit()
        crc_instance.process(data)
        # .hex() provides a string representation of the hex values
        crc_hex = crc_instance.finalbytes().hex().upper()
        # Ensure it is 4 characters long (2 bytes)
        crc_hex = crc_hex.zfill(4)
        # SAS protocol requires the two CRC bytes to be swapped
        return command_hex + crc_hex[2:4] + crc_hex[0:2]
    except Exception as e:
        print(f"[ERROR] CRC calculation failed: {e}")
        return command_hex + "0000"

def get_next_transaction_id():
    """Generates a unique transaction ID for each command."""
    global transaction_id_counter
    transaction_id_counter = (transaction_id_counter + 1) % 10000
    return transaction_id_counter

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("AFT Add Credit Test Application - CORRECTED")
    print("Based on original SAS communication logic")
    print("=" * 60)
    print(f"SAS Port: Will be auto-configured")
    print(f"Asset No: 108 (0x{ASSET_NUMBER})")
    print(f"Registration Key: {REGISTRATION_KEY}")
    print(f"Device Type ID: {DEVICE_TYPE_ID} (detected by main app)")
    print("=" * 60)

# --- Core SAS Communication Functions (Corrected) ---

def open_sas_port():
    """Opens the serial port with the correct SAS settings."""
    global sasport
    if not SAS_PORT:
        print("[ERROR] SAS Port not set. Discovery failed.")
        return False
    try:
        sasport = serial.Serial(
            port=SAS_PORT,
            baudrate=SAS_BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE, # Start with NO parity
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        sasport.dtr = True
        sasport.rts = False
        if sasport.is_open:
            print(f"[INFO] SAS Port {SAS_PORT} opened successfully.")
            
            # CRITICAL: Send AFT registration init command like main app!
            print("[INFO] Sending AFT Registration Init command (017301FFA765)...")
            init_cmd = GetCRC("017301FF")  # AFT registration init
            SendSASPORT(init_cmd)
            time.sleep(0.5)  # Give machine time to respond
            
            # Try to read asset number response
            response = ReadSASPORT()
            if response:
                print(f"[INFO] AFT Registration response: {response}")
                if response.startswith("0173") and len(response) >= 16:
                    asset_hex = response[8:16]
                    print(f"[INFO] Asset number confirmed: {asset_hex}")
            else:
                print("[WARNING] No response to AFT registration init - continuing anyway")
            
            return True
        else:
            print(f"[ERROR] Failed to open SAS Port {SAS_PORT}.")
            return False
    except Exception as e:
        print(f"[ERROR] Could not open port {SAS_PORT}: {e}")
        return False

def SendSASPORT(command_hex):
    """
    Sends a command to the SAS port using the correct parity switching method.
    Device type specific implementation matching the main app exactly.
    """
    if not sasport or not sasport.is_open:
        print("[ERROR] Cannot send command, port is not open.")
        return False

    command_hex = command_hex.replace(" ", "")
    if len(command_hex) < 2:
        return False

    try:
        # Device type specific sending logic - EXACTLY like main app
        if DEVICE_TYPE_ID == 1 or DEVICE_TYPE_ID == 4:
            # Novomatic/Octavian - just send normally with current parity
            data_bytes = bytes.fromhex(command_hex)
            bytes_written = sasport.write(data_bytes)
            sasport.flush()
            print(f"[DEBUG] Sent {bytes_written} bytes (Novomatic mode)")
            return True
        else:
            # Determine sending method like main app
            is_new_sending_msg = 0
            is_communication_by_windows = 1 if platform.system() == "Windows" else 0
            
            if is_communication_by_windows == 1 or DEVICE_TYPE_ID == 11:
                is_new_sending_msg = 1
                
            if DEVICE_TYPE_ID == 6:
                is_new_sending_msg = 0
                
            # CRITICAL: Device type 8 detection shows it uses Windows-style even on Linux!
            # Looking at main app, device type 8 must use the Windows approach
            if DEVICE_TYPE_ID == 8:
                is_new_sending_msg = 1

            if is_new_sending_msg == 1:  # Windows or Interblock
                sleeptime = 0.005
                if DEVICE_TYPE_ID == 11:
                    sleeptime = 0.003
                
                # MARK parity for first byte
                sasport.parity = serial.PARITY_MARK
                sasport.write(bytes.fromhex(command_hex[0:2]))
                sasport.flush()
                time.sleep(sleeptime)
                
                # SPACE parity for rest
                if len(command_hex) > 2:
                    sasport.parity = serial.PARITY_SPACE
                    sasport.write(bytes.fromhex(command_hex[2:]))
                    sasport.flush()
                    
            else:
                # Linux with termios - EXACTLY like main app
                saswaittime = 0.001  # From main app comment: "2020-12-25 test ok gibi.."
                
                iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(sasport.fileno())
                
                CMSPAR = 0x40000000  # EXACTLY like main app
                
                # MARK parity for first byte
                cflag |= termios.PARENB | CMSPAR | termios.PARODD
                termios.tcsetattr(sasport.fileno(), termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
                
                sasport.write(bytes.fromhex(command_hex[0:2]))
                sasport.flush()
                
                if len(command_hex) > 2:
                    time.sleep(saswaittime)
                    
                    # SPACE parity for rest
                    iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(sasport.fileno())
                    cflag |= termios.PARENB
                    cflag &= ~termios.PARODD
                    termios.tcsetattr(sasport.fileno(), termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
                    
                    sasport.write(bytes.fromhex(command_hex[2:]))
                    sasport.flush()
                    
        # CRITICAL: Flush input like original SendSASPORT!
        sasport.flushInput()
        return True
                    
    except Exception as e:
        print(f"[ERROR] Failed to send SAS command: {e}")
        return False


def ReadSASPORT():
    """Reads data from SAS port - EXACTLY like main app's get_data_from_sas_port"""
    if not sasport or not sasport.is_open:
        return ""
        
    try:
        data_left = sasport.in_waiting
        if data_left == 0:
            return ""
            
        out = ''
        read_count_timeout = 3  # From main app
        
        while read_count_timeout > 0:
            read_count_timeout = read_count_timeout - 1
            
            while sasport.in_waiting > 0:
                out += sasport.read_all().hex()  # CRITICAL: read_all() not read()!
                time.sleep(0.005)
        
        return out.upper()
        
    except Exception as e:
        print(f"[ERROR] Failed to read from SAS port: {e}")
        return ""

# --- Command and Response Handling ---

def continuous_polling():
    """Background thread to poll the machine, keeping the connection alive."""
    global polling_active
    print("[INFO] SAS polling thread started.")
    last_poll_type = 81
    while polling_active:
        try:
            # Alternate polls like the original app
            poll_cmd = "80" if last_poll_type == 81 else "81"
            SendSASPORT(GetCRC(SAS_ADDRESS + poll_cmd))
            last_poll_type = int(poll_cmd)

            time.sleep(0.02) # Wait for potential response
            response = ReadSASPORT()
            if response:
                print(f"[POLL RX] {response}")
                handle_received_sas_command(response)
            
            time.sleep(0.2) # Polling interval
        except Exception as e:
            print(f"[ERROR] Polling loop error: {e}")
            time.sleep(1)
    print("[INFO] SAS polling thread stopped.")


def handle_received_sas_command(response_hex):
    """Processes responses from the gaming machine."""
    global aft_response_received, aft_transfer_status, balance_response_received, balance_amount
    
    if not response_hex:
        return

    # Check for AFT Transfer Response (72h)
    if response_hex.startswith("0172"):
        print(f"[AFT RX] Received AFT Response: {response_hex}")
        aft_transfer_status = response_hex[12:14]
        aft_response_received = True

    # Check for Balance Query Response (74h)
    elif response_hex.startswith("0174"):
        print(f"[BALANCE RX] Received Balance Response: {response_hex}")
        try:
            # Cashable amount is 5 bytes BCD, starting at index 22
            cashable_bcd = response_hex[22:32]
            # Convert BCD to integer (each hex digit represents a decimal digit)
            balance_cents = 0
            for i in range(0, len(cashable_bcd), 2):
                if i + 1 < len(cashable_bcd):
                    byte_val = cashable_bcd[i:i+2]
                    high_digit = int(byte_val[0], 16)
                    low_digit = int(byte_val[1], 16)
                    balance_cents = balance_cents * 100 + high_digit * 10 + low_digit
            balance_amount = Decimal(balance_cents) / Decimal(100)
            print(f"[BALANCE RX] Parsed cashable amount: ${balance_amount}")
        except Exception as e:
            print(f"[ERROR] Failed to parse balance: {e}")
        balance_response_received = True
    
    # Check for AFT completion acknowledgement (69h)
    elif response_hex.startswith("01FF69"):
        print("[AFT RX] Received AFT Transfer Complete ACK (69h).")
        # This confirms the machine processed the transfer. We can consider it success.
        aft_transfer_status = "00"
        aft_response_received = True


def send_aft_credit_command(amount_to_load):
    """Constructs and sends the AFT credit command (72h)."""
    print("\n--- Sending AFT Credit Command ---")
    amount_in_cents = int(Decimal(amount_to_load) * 100)
    
    # Body of the command
    command_body = ""
    command_body += "00"  # Transfer Code: 00 (No receipt)
    command_body += "00"  # Transfer Index
    command_body += "00"  # Transfer Type: 00 (Cashable)
    command_body += AddLeftBCD(amount_in_cents, 5)  # 5-byte BCD Cashable amount
    command_body += AddLeftBCD(0, 5)  # 5-byte BCD Restricted amount
    command_body += AddLeftBCD(0, 5)  # 5-byte BCD Non-restricted amount
    command_body += "07"  # Transfer Flags: 07 (Hard cashout mode)
    command_body += ASSET_NUMBER
    command_body += REGISTRATION_KEY
    
    # Transaction ID (ASCII encoded)
    tid = str(get_next_transaction_id())
    tid_hex = tid.encode('utf-8').hex()
    tid_len_hex = f"{len(tid_hex) // 2:02X}"
    
    command_body += tid_len_hex
    command_body += tid_hex
    
    command_body += "00000000"  # Expiration Date
    command_body += "0000"      # Pool ID
    command_body += "00"        # Receipt Data Length

    # Header with length
    command_header = SAS_ADDRESS + "72" + f"{len(command_body) // 2:02X}"

    full_command = GetCRC(command_header + command_body)
    print(f"[AFT TX] Sending command: {full_command}")
    return SendSASPORT(full_command)


def main():
    """Main application flow."""
    global polling_active, sasport, SAS_PORT
    
    print_banner()

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python test_aft_op.py <amount> [port]")
        print("Examples:")
        print("  python test_aft_op.py 100.50")
        print("  python test_aft_op.py 50 /dev/ttyUSB0")
        print("  python test_aft_op.py 25 /dev/ttyUSB1")
        sys.exit(1)
        
    try:
        amount = Decimal(sys.argv[1])
        if amount <= 0:
            raise ValueError("Amount must be positive.")
    except Exception as e:
        print(f"[ERROR] Invalid amount: {e}")
        sys.exit(1)

    # --- Port Configuration ---
    print("\n--- Step 1: Configuring SAS Port ---")
    if len(sys.argv) == 3:
        # Port specified as parameter
        SAS_PORT = sys.argv[2]
        print(f"[INFO] Using specified SAS Port: {SAS_PORT}")
    else:
        # Default port based on previous tests
        SAS_PORT = "/dev/ttyUSB1"  # Based on previous tests, this was the working port
        print(f"[INFO] Using default SAS Port: {SAS_PORT}")
        print(f"[INFO] To specify a different port, use: python test_aft_op.py {amount} /dev/ttyUSB0")
    
    # Validate port exists (basic check)
    import os
    if not os.path.exists(SAS_PORT):
        print(f"[WARNING] Port {SAS_PORT} does not exist!")
        print("[INFO] Available ports:")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(f"  - {port.device}: {port.description}")
        print("[INFO] Continuing anyway - port might become available...")
    
    if not open_sas_port():
        sys.exit(1)

    polling_thread = None
    try:
        # --- Start Polling ---
        print("\n--- Step 2: Starting SAS Polling ---")
        polling_active = True
        polling_thread = threading.Thread(target=continuous_polling, daemon=True)
        polling_thread.start()
        time.sleep(1) # Let polling stabilize

        # --- Send AFT Command ---
        if not send_aft_credit_command(amount):
            print("[ERROR] Failed to send AFT command.")
            raise Exception("AFT Send Failure")
            
        # --- Wait for Response ---
        print("\n--- Step 3: Waiting for AFT Response ---")
        timeout = 10
        start_time = time.time()
        while not aft_response_received and time.time() - start_time < timeout:
            time.sleep(0.1)

        if not aft_response_received:
            print("[ERROR] Timeout: No response received for AFT command.")
        elif aft_transfer_status == "00":
            print("[SUCCESS] AFT Transfer successful!")
        else:
            print(f"[FAILURE] AFT Transfer failed with status code: {aft_transfer_status}")
            
    except Exception as e:
        print(f"\n[FATAL] An error occurred: {e}")
    finally:
        # --- Cleanup ---
        print("\n--- Step 4: Cleaning up ---")
        if polling_thread:
            polling_active = False
            polling_thread.join(timeout=2)
        if sasport and sasport.is_open:
            sasport.close()
            print("[INFO] SAS Port closed.")
        print("Test finished.")


if __name__ == "__main__":
    main()
