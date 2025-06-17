#!/usr/bin/env python3
"""
AFT Add Credit Test Application
Based on the original SAS communication logic from raspberryPython_orj.py.ref
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
import threading
from decimal import Decimal
from crccheck.crc import CrcKermit

# Configuration - hardcoded as requested
SAS_PORT = "/dev/ttyUSB1"
SAS_BAUDRATE = 19200
SAS_ADDRESS = "01"  # Address
ASSET_NUMBER = "6C000000"  # Asset 108 in hex, padded to 4 bytes
REGISTRATION_KEY = "000000000000000000000000000000000000000000"  # All zeros, 20 bytes
CASHOUT_MODE_SOFT = False  # Use hard cashout mode

# Global variables - matching original code
sasport = None
transaction_id = 1
IsWaitingForParaYukle = False
last_sent_poll_type = 81  # Sas_LastSent equivalent
polling_active = False
polling_thread = None

# AFT response tracking
aft_transfer_status = "FF"  # Transfer status like original
aft_response_received = False

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("AFT Add Credit Test Application")
    print("Based on raspberryPython_orj.py.ref - EXACT MATCH")
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
    """Open SAS serial port - EXACTLY like original"""
    global sasport
    try:
        sasport = serial.Serial()
        sasport.port = SAS_PORT
        sasport.baudrate = SAS_BAUDRATE
        sasport.parity = serial.PARITY_NONE
        sasport.stopbits = serial.STOPBITS_ONE
        sasport.bytesize = serial.EIGHTBITS
        sasport.timeout = 0.1
        sasport.xonxoff = False
        sasport.rtscts = False
        sasport.dsrdtr = False
        
        # DTR/RTS settings from original
        sasport.dtr = True
        sasport.rts = False
        
        print(f"Opening SAS port: {SAS_PORT} at {SAS_BAUDRATE} baud...")
        sasport.open()
        
        if sasport.isOpen():
            print("✓ SAS port opened successfully")
            # Initial poll like original
            SendSASPORT("80")
            time.sleep(0.05)
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

def SendSASPORT(command_hex):
    """Send raw hex to SAS port - EXACTLY like original SendSASPORT"""
    global sasport
    if not sasport or not sasport.isOpen():
        return
        
    try:
        data_bytes = bytes.fromhex(command_hex)
        sasport.write(data_bytes)
    except Exception as e:
        print(f"Error in SendSASPORT: {e}")

def SendSASCommand(command_hex):
    """Send SAS command - EXACTLY matching original SendSASCommand"""
    global last_sent_poll_type
    
    command_hex = command_hex.replace(" ", "")
    
    # Update last sent times like original
    if command_hex == "81":
        last_sent_poll_type = 81
    if command_hex == "80":
        last_sent_poll_type = 80

    # Log only important commands (not regular polls)
    if command_hex not in ["80", "81"]:
        print("TX: ", command_hex, datetime.datetime.now())
    
    # Just send normally (device type 8 - default)
    SendSASPORT(command_hex)

def GetDataFromSasPort():
    """Receive data - EXACTLY like original GetDataFromSasPort"""
    global sasport
    if not sasport or not sasport.isOpen():
        return ""
        
    try:
        data_left = sasport.in_waiting
        if data_left == 0:
            return ""
        
        out = ''
        ReadCountTimeOut = 4  # From original
        
        while ReadCountTimeOut > 0:
            ReadCountTimeOut = ReadCountTimeOut - 1
            
            while sasport.in_waiting > 0:
                out += sasport.read_all().hex()
                time.sleep(0.005)
        
        return out.upper()
        
    except Exception as e:
        print(f"Error in GetDataFromSasPort: {e}")
        return ""

def SendGeneralPoll():
    """Send general poll - alternating 80/81 like original"""
    global last_sent_poll_type
    
    # Alternate between 80 and 81 like original
    if last_sent_poll_type == 80:
        poll_command = "81"
    else:
        poll_command = "80"
        
    SendSASCommand(poll_command)

def sas_polling_loop():
    """SAS polling loop - EXACTLY like original main loop"""
    global polling_active, aft_transfer_status, aft_response_received
    
    print("🔄 Starting SAS polling loop...")
    
    while polling_active:
        try:
            # Send general poll
            SendGeneralPoll()
            
            # Check for response like original
            time.sleep(0.05)  # Give time for response
            response = GetDataFromSasPort()
            
            if response:
                # Handle AFT responses - EXACTLY like original
                if response[0:4] == "0172":
                    print(f"RX: {response}")
                    print("📊 AFT Transfer Response Received!")
                    Yanit_ParaYukle(response)
                elif response.startswith("01FF69DB5B") or response == "FF69DB5B" or response == "69DB5B" or response == "69":
                    print(f"RX: {response}")
                    print("✓ AFT completion notification received!")
                    aft_transfer_status = "00"  # Success like original
                    aft_response_received = True
                elif response == "01" or response == "00":
                    # Normal responses - continue polling silently
                    pass
                else:
                    # Other responses - log them
                    print(f"RX: {response}")
                    print(f"Other response: {response}")
            
            # Schedule next poll like original (40ms interval)
            time.sleep(0.04)
            
        except Exception as e:
            print(f"✗ Polling error: {e}")
            time.sleep(0.1)
    
    print("🔄 Polling stopped")

def start_polling():
    """Start continuous polling"""
    global polling_active, polling_thread
    
    if not polling_active:
        polling_active = True
        polling_thread = threading.Thread(target=sas_polling_loop, daemon=True)
        polling_thread.start()
        time.sleep(0.5)  # Give polling time to start

def stop_polling():
    """Stop continuous polling"""
    global polling_active, polling_thread
    
    if polling_active:
        polling_active = False
        if polling_thread:
            polling_thread.join(timeout=2)

def Yanit_ParaYukle(response):
    """Parse AFT response - EXACTLY like original Yanit_ParaYukle"""
    global aft_transfer_status, aft_response_received
    
    try:
        print(f"📥 ========== AFT TRANSFER RESPONSE ==========")
        print(f"📥 RAW RESPONSE: {response}")
        print(f"===============================================")
        
        if len(response) < 14:
            print("Response too short")
            aft_transfer_status = "FF"
            aft_response_received = True
            return
            
        # Parse like original - extract transfer status at position 12:14
        transfer_status = response[12:14]  # Position 12-13 in response (CORRECTED)
        aft_transfer_status = transfer_status
        
        # Check for successful AFT load statuses like original
        if transfer_status == "00" or transfer_status == "10" or transfer_status == "11":
            print(f"✅ AFT Transfer SUCCESSFUL! Status: {transfer_status}")
            aft_response_received = True
        elif transfer_status == "C0":
            print(f"⏳ AFT Transfer PENDING! Status: {transfer_status}")
            # Don't set response_received = True for C0, keep waiting
        else:
            print(f"❌ AFT Transfer FAILED! Status: {transfer_status}")
            aft_response_received = True
        
        # Status descriptions from original
        status_descriptions = {
            "00": "Transfer successful",
            "10": "Transfer successful (partial)",
            "11": "Transfer successful (bonus/jackpot)",
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
        
        status_msg = status_descriptions.get(transfer_status, f"Unknown: {transfer_status}")
        print(f"📥 Transfer Status: {transfer_status} - {status_msg}")
        
        print(f"===============================================")
        
    except Exception as e:
        print(f"✗ Error parsing AFT response: {e}")
        aft_transfer_status = "FF"
        aft_response_received = True

def Komut_ParaYukle(amount):
    """Build AFT credit loading command - EXACTLY like original Komut_ParaYukle"""
    global transaction_id
    
    print(f"Building AFT command for amount: {amount}")
    
    # Convert amount to cents (BCD format) - EXACTLY like original
    customerbalanceint = int(float(amount) * 100)
    
    print(f"Amount in cents: {customerbalanceint}")
    
    # Command Header - EXACTLY like original
    CommandHeader = SAS_ADDRESS      # 1-Address  01
    CommandHeader += "72"            # 1-Command  72 (AFT transfer to gaming machine)
    # Length will be added later
    
    # Command Body - EXACTLY like original
    Command = ""
    Command += "00"                  # 1-Transfer Code    00
    Command += "00"                  # 1-Transfer Index   00
    Command += "00"                  # 1-Transfer Type    00 (cashable amount)
    
    # Amount fields (5 bytes each in BCD) - EXACTLY like original
    Command += AddLeftBCD(customerbalanceint, 5)  # 5-Cashable amount (BCD)
    Command += AddLeftBCD(0, 5)                   # 5-Restricted amount (BCD)
    Command += AddLeftBCD(0, 5)                   # 5-Nonrestricted amount (BCD)
    
    # Transfer flags - EXACTLY like original
    if CASHOUT_MODE_SOFT:
        Command += "03"              # 1-Transfer flag (soft cashout)
    else:
        Command += "07"              # 1-Transfer flag (hard cashout)
    
    # Asset number and registration - EXACTLY like original
    Command += ASSET_NUMBER          # 4-Asset number
    Command += REGISTRATION_KEY      # 20-Registration key
    
    # Transaction ID - EXACTLY like original
    TRANSACTIONID = "".join("{:02x}".format(ord(c)) for c in str(transaction_id))
    Command += AddLeftBCD(int(len(TRANSACTIONID) / 2), 1)  # 1-TransactionId Length
    Command += TRANSACTIONID         # X-TransactionID
    
    # Expiration date - EXACTLY like original
    Command += "00000000"            # 4-ExpirationDate (BCD) MMDDYYYY
    
    # Pool ID - EXACTLY like original
    Command += "0000"                # 2-Pool ID
    
    # Receipt data - EXACTLY like original
    Command += "00"                  # 1-Receipt data length
    # No receipt data
    # No lock timeout
    
    # Add length to header - EXACTLY like original
    CommandHeader += hex(int(len(Command) / 2)).replace("0x", "").upper().zfill(2)
    
    # Complete command - EXACTLY like original
    GenelKomut = CommandHeader + Command
    
    # Add CRC - EXACTLY like original
    GenelKomut = GetCRC(GenelKomut)
    
    print(f"Final AFT command: {GenelKomut}")
    print(f"Command length: {len(GenelKomut)} hex chars ({len(GenelKomut)//2} bytes)")
    
    return GenelKomut

def wait_for_aft_completion():
    """Wait for AFT completion - like original"""
    global aft_response_received, aft_transfer_status
    
    print("Waiting for AFT completion...")
    
    timeout = 30  # 30 seconds timeout
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if aft_response_received:
            if aft_transfer_status in ["00", "10", "11"]:
                print(f"✓ AFT transfer completed successfully! Status: {aft_transfer_status}")
                return True
            else:
                print(f"✗ AFT transfer failed with status: {aft_transfer_status}")
                return False
        
        time.sleep(0.1)
    
    print("✗ Timeout waiting for AFT completion")
    return False

def main():
    """Main function"""
    global IsWaitingForParaYukle, transaction_id, aft_response_received, aft_transfer_status
    
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
        # Start continuous polling like original
        print("\n--- Step 1: Start SAS Polling ---")
        start_polling()
        
        # Wait for communication to establish
        time.sleep(2)
        
        # Build and send AFT command like original
        print("\n--- Step 2: Send AFT Credit Command ---")
        aft_command = Komut_ParaYukle(amount)
        
        # Reset tracking variables
        IsWaitingForParaYukle = True
        aft_response_received = False
        aft_transfer_status = "FF"
        
        # Send AFT command like original
        print(f"TX -> AFT Credit Load: {aft_command}")
        SendSASCommand(aft_command)
        
        # Wait for completion like original
        print("\n--- Step 3: Wait for AFT Completion ---")
        if wait_for_aft_completion():
            print("✓ AFT operation completed successfully!")
        else:
            print("✗ AFT operation failed or timed out")
        
        IsWaitingForParaYukle = False
        
        # Increment transaction ID for next use like original
        transaction_id += 1
        if transaction_id > 1000:
            transaction_id = 1
            
    except KeyboardInterrupt:
        print("\n✗ Operation interrupted by user")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        # Stop polling
        stop_polling()
        close_sas_port()
        print("\nAFT test completed.")

if __name__ == "__main__":
    main()
