import uuid
import socket
import netifaces
from crccheck.crc import CrcKermit


def get_mac_address(interface='eth0'):
    """Get the MAC address of a network interface (default: eth0)."""
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
    except Exception:
        return None


def get_ip_address():
    """Get the primary IP address of the machine."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return None


def generate_pi_id():
    """Generate a unique Pi ID (UUID4)."""
    return str(uuid.uuid4())


def get_asset_number():
    """Placeholder for getting the slot machine asset number. Implement using SASCommunicator logic."""
    # TODO: Implement this using your SASCommunicator logic
    return None


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


def read_asset_to_int(d):
    """Convert a hex asset string to int, reversing bytes as needed."""
    hexa_string = d
    if len(hexa_string) % 2 != 0:
        hexa_string = "0" + hexa_string
    reversed_hexa_string = ""
    i = len(hexa_string) - 2
    while i >= 0:
        reversed_hexa_string = reversed_hexa_string + hexa_string[i:i+2]
        i = i - 2
    return int(reversed_hexa_string, 16)


def add_left_bcd(number_str, length_bytes):
    """
    Pads a number string with leading '00' to reach target byte length.
    This matches the original working implementation (AddLeftBCD + AddLeftString).
    
    Note: Despite the name "BCD", this function does NOT do true BCD encoding.
    It just does string padding, which is what the original working code did.
    """
    # Convert to integer first to remove any leading zeros, then back to string
    number_str = str(int(number_str))
    
    # Ensure even number of digits
    if len(number_str) % 2 != 0:
        number_str = "0" + number_str
    
    # Calculate current length in bytes
    current_len_bytes = len(number_str) // 2
    
    # Add left padding with "00" if needed
    if current_len_bytes < length_bytes:
        padding_needed_bytes = length_bytes - current_len_bytes
        return "00" * int(padding_needed_bytes) + number_str
    elif current_len_bytes > length_bytes:
        # Truncate if too long (take rightmost bytes)
        return number_str[-(length_bytes * 2):]
    else:
        return number_str 