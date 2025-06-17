#!/usr/bin/env python3
"""
AFT Add Credit Test Application
Based on raspberryPython_orj.py.ref
For testing AFT operations on Raspberry Pi

Usage: python3 test_aft_op.py <amount>
Example: python3 test_aft_op.py 100.50

SAS Port: /dev/ttyUSB1
Asset No: 108 (0x6C)
Registration Key: all zeros (000000000000000000000000000000000000000000)
"""

import serial
import sys
import datetime
import time
from decimal import Decimal
from crccheck.crc import CrcKermit

# Configuration - hardcoded as requested
SAS_PORT = "/dev/ttyUSB1"
SAS_BAUDRATE = 19200
SAS_ADDRESS = "01"  # Address
ASSET_NUMBER = "6C000000"  # Asset 108 in hex, padded to 4 bytes
REGISTRATION_KEY = "000000000000000000000000000000000000000000"  # All zeros, 20 bytes
CASHOUT_MODE_SOFT = False  # Use hard cashout mode

# Global variables
sasport = None
transaction_id = 1
IsWaitingForParaYukle = False

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("AFT Add Credit Test Application")
    print("Based on raspberryPython_orj.py.ref")
    print("=" * 60)
    print(f"SAS Port: {SAS_PORT}")
    print(f"Asset No: 108 (0x{ASSET_NUMBER})")
    print(f"Registration Key: {REGISTRATION_KEY}")
    print("=" * 60)

def AddLeftString(text, eklenecek, kacadet):
    """Add string to left - utility function from original"""
    while kacadet > 0:
        text = eklenecek + text
        kacadet = kacadet - 1
    return text

def AddLeftBCD(numbers, leng):
    """Convert number to BCD format - from original"""
    numbers = int(numbers)
    retdata = str(numbers)
    
    if len(retdata) % 2 == 1:
        retdata = "0" + retdata
    
    countNumber = len(retdata) / 2
    kalan = int(leng - countNumber)
    
    retdata = AddLeftString(retdata, "00", kalan)
    return retdata

def GetCRC(komut):
    """Calculate CRC using Kermit - from original"""
    data = bytearray.fromhex(komut)
    crcinst = CrcKermit()
    crcinst.process(data)
    CRCsi = crcinst.finalbytes().hex()
    CRCsi = str(CRCsi).replace("0x", "").upper().replace("\\X", "").replace("B'", "").replace("<", "").replace("'", "")
    
    if len(CRCsi) == 1:
        CRCsi = "0" + CRCsi
    if len(CRCsi) == 2:
        CRCsi = "00" + CRCsi
    if len(CRCsi) == 3:
        CRCsi = "0" + CRCsi
    
    retdata = komut + CRCsi[2:4] + CRCsi[0:2]
    return retdata

def open_sas_port():
    """Open SAS serial port"""
    global sasport
    try:
        sasport = serial.Serial()
        sasport.port = SAS_PORT
        sasport.baudrate = SAS_BAUDRATE
        sasport.parity = serial.PARITY_NONE
        sasport.stopbits = serial.STOPBITS_ONE
        sasport.bytesize = serial.EIGHTBITS
        sasport.timeout = 1
        
        print(f"Opening SAS port: {SAS_PORT} at {SAS_BAUDRATE} baud...")
        sasport.open()
        
        if sasport.isOpen():
            print("✓ SAS port opened successfully")
            return True
        else:
            print("✗ Failed to open SAS port")
            return False
            
    except Exception as e:
        print(f"✗ Error opening SAS port: {e}")
        return False

def close_sas_port():
    """Close SAS serial port"""
    global sasport
    try:
        if sasport and sasport.isOpen():
            sasport.close()
            print("✓ SAS port closed")
    except Exception as e:
        print(f"✗ Error closing SAS port: {e}")

def send_command(command_name, command_hex):
    """Send SAS command - from original"""
    global sasport
    try:
        if not sasport or not sasport.isOpen():
            print("✗ SAS port not open")
            return False
            
        # Convert hex string to bytes
        if len(command_hex) % 2 != 0:
            print("✗ Invalid command length")
            return False
            
        command_bytes = bytes.fromhex(command_hex)
        
        print(f"TX -> {command_name}: {command_hex}")
        
        # Send command
        sasport.write(command_bytes)
        sasport.flush()
        
        # Wait for response
        time.sleep(0.1)
        
        # Read response
        response = read_sas_response()
        if response:
            print(f"RX <- Response: {response}")
            return True
        else:
            print("No response received")
            return False
            
    except Exception as e:
        print(f"✗ Error sending command: {e}")
        return False

def read_sas_response():
    """Read SAS response - simplified version from original"""
    global sasport
    try:
        if not sasport or not sasport.isOpen():
            return ""
            
        out = ''
        read_timeout = 3
        while read_timeout > 0:
            read_timeout -= 1
            
            while sasport.inWaiting() > 0:
                data = sasport.read_all()
                if data:
                    out += data.hex()
                time.sleep(0.005)
            
            if out:
                break
            time.sleep(0.005)
        
        return out.upper()
        
    except Exception as e:
        print(f"✗ Error reading response: {e}")
        return ""

def hex_to_decimal(hex_str):
    """Convert BCD hex string to decimal - from original"""
    try:
        return int(hex_str) / 100.0
    except:
        return 0.0

def get_transfer_status_description(status_code):
    """Get description for transfer status codes - from original"""
    status_descriptions = {
        "00": "Transfer successful",
        "81": "TransactionID is not unique",
        "83": "Not a valid transfer function", 
        "84": "Cannot transfer large amount to gaming machine",
        "85": "Balance not compatible with denomination",
        "87": "Door open, tilt, or disabled",
        "89": "Registration key doesn't match",
        "93": "Asset number zero or doesn't match",
        "94": "Gaming machine not locked for transfer",
        "95": "TransactionID is not unique (Megajack)",
        "C0": "Not compatible with current transfer in progress",
        "C1": "Unsupported transfer code",
        "FF": "No transfer information available",
        "40": "Transfer pending"
    }
    return status_descriptions.get(status_code, f"Unknown status: {status_code}")

def parse_aft_response(response):
    """Parse AFT response - based on Yanit_ParaYukle from original"""
    try:
        if len(response) < 10:
            return None
            
        print("\n--- AFT Response Analysis ---")
        print(f"Raw response: {response}")
        
        index = 0
        
        # Address
        address = response[index:index+2]
        index += 2
        print(f"Address: {address}")
        
        # Command  
        command = response[index:index+2]
        index += 2
        print(f"Command: {command}")
        
        # Length
        length = response[index:index+2]
        index += 2
        print(f"Length: {length}")
        
        # Transaction Buffer
        transaction_buffer = response[index:index+2]
        index += 2
        print(f"Transaction Buffer: {transaction_buffer}")
        
        # Transfer Status (most important)
        transfer_status = response[index:index+2]
        index += 2
        print(f"Transfer Status: {transfer_status}")
        print(f"Status Description: {get_transfer_status_description(transfer_status)}")
        
        # Receipt Status
        receipt_status = response[index:index+2]
        index += 2
        print(f"Receipt Status: {receipt_status}")
        
        # Transfer Type
        transfer_type = response[index:index+2]
        index += 2
        print(f"Transfer Type: {transfer_type}")
        
        # Amounts (5 bytes each in BCD)
        if index + 30 <= len(response):
            cashable_amount_hex = response[index:index+10]
            index += 10
            cashable_amount = hex_to_decimal(cashable_amount_hex)
            print(f"Cashable Amount: {cashable_amount:.2f} (hex: {cashable_amount_hex})")
            
            restricted_amount_hex = response[index:index+10]
            index += 10
            restricted_amount = hex_to_decimal(restricted_amount_hex)
            print(f"Restricted Amount: {restricted_amount:.2f} (hex: {restricted_amount_hex})")
            
            nonrestricted_amount_hex = response[index:index+10]
            index += 10
            nonrestricted_amount = hex_to_decimal(nonrestricted_amount_hex)
            print(f"Non-restricted Amount: {nonrestricted_amount:.2f} (hex: {nonrestricted_amount_hex})")
        
        # Transfer Flag
        if index + 2 <= len(response):
            transfer_flag = response[index:index+2]
            index += 2
            print(f"Transfer Flag: {transfer_flag}")
        
        # Asset Number
        if index + 8 <= len(response):
            asset_number = response[index:index+8]
            index += 8
            print(f"Asset Number: {asset_number}")
        
        # Transaction ID
        if index + 2 <= len(response):
            try:
                transaction_id_length = int(response[index:index+2], 16) * 2
                index += 2
                if index + transaction_id_length <= len(response):
                    transaction_id_hex = response[index:index+transaction_id_length]
                    index += transaction_id_length
                    # Convert hex to string
                    transaction_id = ''.join(chr(int(transaction_id_hex[i:i+2], 16)) for i in range(0, len(transaction_id_hex), 2))
                    print(f"Transaction ID: {transaction_id}")
            except:
                print("Could not parse transaction ID")
        
        print("--- End AFT Response Analysis ---\n")
        
        return {
            'status': transfer_status,
            'success': transfer_status == "00",
            'description': get_transfer_status_description(transfer_status)
        }
        
    except Exception as e:
        print(f"✗ Error parsing AFT response: {e}")
        return None

def build_aft_command(amount):
    """Build AFT credit loading command - from original Komut_ParaYukle"""
    global transaction_id
    
    print(f"Building AFT command for amount: {amount}")
    
    # Convert amount to cents (BCD format)
    customerbalanceint = int(float(amount) * 100)
    
    print(f"Amount in cents: {customerbalanceint}")
    
    # Command Header
    CommandHeader = SAS_ADDRESS      # 1-Address  01
    CommandHeader += "72"            # 1-Command  72 (AFT transfer to gaming machine)
    # Length will be added later
    
    # Command Body
    Command = ""
    Command += "00"                  # 1-Transfer Code    00
    Command += "00"                  # 1-Transfer Index   00
    Command += "00"                  # 1-Transfer Type    00 (cashable amount)
    
    # Amount fields (5 bytes each in BCD)
    Command += AddLeftBCD(customerbalanceint, 5)  # 5-Cashable amount (BCD)
    Command += AddLeftBCD(0, 5)                   # 5-Restricted amount (BCD)
    Command += AddLeftBCD(0, 5)                   # 5-Nonrestricted amount (BCD)
    
    # Transfer flags
    if CASHOUT_MODE_SOFT:
        Command += "03"              # 1-Transfer flag (soft cashout)
    else:
        Command += "07"              # 1-Transfer flag (hard cashout)
    
    # Asset number and registration
    Command += ASSET_NUMBER          # 4-Asset number
    Command += REGISTRATION_KEY      # 20-Registration key
    
    # Transaction ID
    TRANSACTIONID = "".join("{:02x}".format(ord(c)) for c in str(transaction_id))
    Command += AddLeftBCD(int(len(TRANSACTIONID) / 2), 1)  # 1-TransactionId Length
    Command += TRANSACTIONID         # X-TransactionID
    
    # Expiration date (set to zeros for no expiration)
    Command += "00000000"            # 4-ExpirationDate (BCD) MMDDYYYY
    
    # Pool ID
    Command += "0000"                # 2-Pool ID
    
    # Receipt data
    Command += "00"                  # 1-Receipt data length
    # No receipt data
    # No lock timeout
    
    # Add length to header
    CommandHeader += hex(int(len(Command) / 2)).replace("0x", "").upper().zfill(2)
    
    # Complete command
    GenelKomut = CommandHeader + Command
    
    # Add CRC
    GenelKomut = GetCRC(GenelKomut)
    
    print(f"Final AFT command: {GenelKomut}")
    print(f"Command length: {len(GenelKomut)} hex chars ({len(GenelKomut)//2} bytes)")
    
    return GenelKomut

def wait_for_aft_response():
    """Wait for AFT completion response"""
    print("Waiting for AFT response...")
    
    timeout = 30  # 30 seconds timeout
    start_time = time.time()
    aft_result = None
    
    while time.time() - start_time < timeout:
        response = read_sas_response()
        if response:
            print(f"Received: {response}")
            
            # Check for AFT transfer response (command 0x72)
            if response.startswith("0172"):
                print("📊 AFT Transfer Response Received!")
                aft_result = parse_aft_response(response)
                if aft_result:
                    if aft_result['success']:
                        print("✓ AFT transfer completed successfully!")
                        return True
                    else:
                        print(f"✗ AFT transfer failed: {aft_result['description']}")
                        return False
            
            # Check for AFT completion notification (command 0x69)
            elif "FF69" in response:
                print("✓ AFT completion notification received!")
                if aft_result and aft_result['success']:
                    return True
            
            # Check for other responses
            elif response.startswith("01"):
                print(f"SAS response: {response}")
        
        time.sleep(0.1)
    
    print("✗ Timeout waiting for AFT response")
    return False

def send_interrogation():
    """Send interrogation command (0x2F) - from original"""
    print("Sending interrogation command...")
    
    command = SAS_ADDRESS + "2F"
    command = GetCRC(command)
    
    return send_command("Interrogation", command)

def main():
    """Main function"""
    print_banner()
    
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python3 test_aft_op.py <amount>")
        print("Example: python3 test_aft_op.py 100.50")
        sys.exit(1)
    
    try:
        amount = float(sys.argv[1])
        if amount <= 0:
            print("✗ Amount must be positive")
            sys.exit(1)
    except ValueError:
        print("✗ Invalid amount format")
        sys.exit(1)
    
    print(f"Amount to load: {amount}")
    
    # Open SAS port
    if not open_sas_port():
        sys.exit(1)
    
    try:
        # Send initial interrogation
        print("\n--- Step 1: Initial Interrogation ---")
        send_interrogation()
        time.sleep(0.5)
        
        # Build and send AFT command
        print("\n--- Step 2: Send AFT Credit Command ---")
        aft_command = build_aft_command(amount)
        
        global IsWaitingForParaYukle
        IsWaitingForParaYukle = True
        
        if send_command("AFT Credit Load", aft_command):
            print("✓ AFT command sent successfully")
            
            # Wait for completion
            print("\n--- Step 3: Wait for AFT Completion ---")
            if wait_for_aft_response():
                print("✓ AFT operation completed successfully!")
            else:
                print("✗ AFT operation may have failed or timed out")
        else:
            print("✗ Failed to send AFT command")
        
        # Send final interrogation
        print("\n--- Step 4: Final Interrogation ---")
        send_interrogation()
        time.sleep(0.5)
        
        IsWaitingForParaYukle = False
        
        # Increment transaction ID for next use
        global transaction_id
        transaction_id += 1
        if transaction_id > 1000:
            transaction_id = 1
            
    except KeyboardInterrupt:
        print("\n✗ Operation interrupted by user")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        close_sas_port()
        print("\nAFT test completed.")

if __name__ == "__main__":
    main()
