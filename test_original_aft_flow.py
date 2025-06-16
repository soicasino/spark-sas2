import serial
import time
import argparse
from binascii import unhexlify
from datetime import datetime

# --- CRC Calculation Function (from original source) ---
# This function is crucial for generating the checksum required by the SAS protocol.
# The original code used a library, but I've implemented the CRC-Kermit algorithm directly
# to keep this a single-file application.
def crc_kermit(data):
    """
    Calculates the CRC-Kermit checksum for a byte array.
    """
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc

def get_crc(command_hex):
    """
    Takes a hex command string, calculates its CRC, and returns the full
    command with the CRC appended in the correct byte order.
    """
    # Convert the hex string to a byte array
    data = unhexlify(command_hex)
    
    # Calculate the CRC
    crc_val = crc_kermit(data)
    
    # Get the CRC as a two-byte hex string (e.g., 0x1234 -> "1234")
    crc_hex = format(crc_val, '04x')
    
    # The SAS protocol requires the CRC bytes to be swapped (little-endian)
    crc_swapped = crc_hex[2:4] + crc_hex[0:2]
    
    # Append the swapped CRC to the original command
    full_command = command_hex + crc_swapped
    return full_command.upper()

# --- Helper Functions (from original source) ---

def add_left_bcd(number, length):
    """
    Formats a number into a BCD (Binary-Coded Decimal) string of a specific length,
    padding with '00' on the left if necessary.
    Example: add_left_bcd(10000, 5) -> "0001000000" for $100.00
    """
    s_number = str(int(number))
    # Pad with a leading zero if the number of digits is odd
    if len(s_number) % 2 != 0:
        s_number = "0" + s_number
    
    # Pad with "00" bytes to reach the desired byte length
    while len(s_number) < length * 2:
        s_number = "00" + s_number
        
    return s_number

def decode_to_hex(s):
    """
    Converts a string into a byte array from its hex representation.
    """
    return unhexlify(s)

def log_ts(message):
    """Prints a message with a timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {message}")

def parse_balance_response(response_hex):
    """Parses the response from a 0x74 command to extract balance info."""
    log_ts("Parsing balance response...")
    try:
        # Check if the response is for a 0x74 command and is of minimum length
        if not response_hex.startswith("0174") or len(response_hex) < 54:
            log_ts("  > Response is not a valid 0x74 balance response.")
            return

        # Extract balance fields based on SAS 6.02 specification for command 74h
        # Response structure: Address(1) + Command(1) + Length(1) + ...
        # Current Cashable Amount is 5 bytes BCD, starting at byte 12 (index 24)
        cashable_hex = response_hex[24:34]
        restricted_hex = response_hex[34:44]
        non_restricted_hex = response_hex[44:54]

        # Convert BCD to decimal amount
        cashable_amount = int(cashable_hex) / 100.0
        restricted_amount = int(restricted_hex) / 100.0
        non_restricted_amount = int(non_restricted_hex) / 100.0
        
        print("-" * 50)
        log_ts("Machine Balance:")
        log_ts(f"  > Cashable:       ${cashable_amount:.2f}")
        log_ts(f"  > Restricted:     ${restricted_amount:.2f}")
        log_ts(f"  > Non-Restricted: ${non_restricted_amount:.2f}")
        print("-" * 50)

    except Exception as e:
        log_ts(f"  > Error parsing balance response: {e}")

# --- Main Execution Logic ---

def execute_aft_transfer(port_name):
    """
    The main logic for opening the serial port and sending the AFT command.
    """
    sas_port = None
    transaction_id = 1 # Start with transaction ID 1
    
    try:
        log_ts(f"Attempting to open port: {port_name}...")
        # Configure and open the serial port
        sas_port = serial.Serial(
            port=port_name,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        log_ts(f"Port {port_name} opened successfully.")
        
        # --- STEP 1: Construct and Send the AFT Transfer Command (0x72) ---
        log_ts("Constructing AFT command (0x72)...")
        
        machine_address = "01" 
        command_code = "72"
        
        transfer_code = "00"
        transfer_index = "00"
        transfer_type = "00"
        cashable_amount = add_left_bcd(10000, 5) # $100.00
        restricted_amount = add_left_bcd(0, 5)
        non_restricted_amount = add_left_bcd(0, 5)
        transfer_flags = "07"
        asset_number = "6C000000" # Asset no 108
        registration_key = "0" * 40
        
        s_transaction_id = str(transaction_id)
        transaction_id_hex = s_transaction_id.encode().hex()
        transaction_id_len = format(len(s_transaction_id), '02x')
        
        expiration_date = "00000000"
        pool_id = "0000"
        receipt_data_len = "00"
        
        payload = (
            transfer_code + transfer_index + transfer_type +
            cashable_amount + restricted_amount + non_restricted_amount +
            transfer_flags + asset_number + registration_key +
            transaction_id_len + transaction_id_hex +
            expiration_date + pool_id + receipt_data_len
        )
        
        length_hex = format(len(payload) // 2, '02x')
        command_to_crc = machine_address + command_code + length_hex + payload
        full_command_72 = get_crc(command_to_crc)
        
        print("-" * 50)
        log_ts(f"AFT Command to send (TX): {full_command_72}")
        print("-" * 50)
        
        log_ts("Sending AFT command...")
        sas_port.write(decode_to_hex(full_command_72))
        
        log_ts("Command sent. Waiting for response...")
        time.sleep(0.5)
        response = sas_port.read(128)
        if response:
            log_ts(f"AFT Response received (RX): {response.hex().upper()}")
        else:
            log_ts("No response from AFT command.")
            
        # --- STEP 2: Construct and Send the Balance Query Command (0x74) ---
        log_ts("Waiting 1 second before querying balance...")
        time.sleep(1)

        log_ts("Constructing Balance Query command (0x74)...")
        balance_query_command = get_crc("017400000000")

        print("-" * 50)
        log_ts(f"Balance Query to send (TX): {balance_query_command}")
        print("-" * 50)

        log_ts("Sending balance query...")
        sas_port.write(decode_to_hex(balance_query_command))
        log_ts("Query sent. Waiting for response...")
        time.sleep(0.5)
        
        balance_response = sas_port.read(128)
        if balance_response:
            log_ts(f"Balance Response received (RX): {balance_response.hex().upper()}")
            parse_balance_response(balance_response.hex().upper())
        else:
            log_ts("No response from balance query.")

    except serial.SerialException as e:
        print(f"\n[ERROR] Serial Port Error: {e}")
        print("        Please check the port name and ensure the device is connected.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        if sas_port and sas_port.is_open:
            sas_port.close()
            log_ts(f"Port {port_name} closed.")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="SAS AFT Terminal Tester for Raspberry Pi.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "port", 
        nargs='?', 
        default="/dev/ttyUSB1", 
        help="The serial port to use.\nDefaults to /dev/ttyUSB1 if not provided."
    )
    args = parser.parse_args()
    
    # Execute the transfer and balance check
    execute_aft_transfer(args.port)
