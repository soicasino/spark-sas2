#!/usr/bin/env python3
"""
AFT Add Credit Test Application
Based on the original SAS communication logic from raspberryPython_orj.py.ref
For testing AFT operations on Raspberry Pi

Usage: python3 test_aft_op.py <amount>
Example: python3 test_aft_op.py 100.50

SAS Port: /dev/ttyUSB0
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
SAS_PORT = "/dev/ttyUSB0"
SAS_BAUDRATE = 19200
SAS_ADDRESS = "01"  # Address
ASSET_NUMBER = "6C000000"  # Asset 108 in hex, padded to 4 bytes
REGISTRATION_KEY = "000000000000000000000000000000000000000000"  # All zeros, 20 bytes
CASHOUT_MODE_SOFT = False  # Use hard cashout mode

# Transaction ID management - EXACTLY like main app
import datetime
current_transaction_id = int(datetime.datetime.now().timestamp()) % 10000

def get_next_transaction_id():
    """Get the next transaction ID, incrementing the internal counter - EXACTLY like main app"""
    global current_transaction_id
    current_transaction_id = (current_transaction_id + 1) % 10000
    return current_transaction_id

# Global variables - matching original code
sasport = None
transaction_id = 1
IsWaitingForParaYukle = False
last_sent_poll_type = 80
polling_active = False
polling_thread = None

# AFT response tracking
aft_transfer_status = None
aft_response_received = False
balance_response_received = False
balance_amount = 0.0

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

def GetCRC(command):
    """Calculate CRC for SAS command - EXACTLY matching original"""
    try:
        data = bytearray.fromhex(command)
        crc_instance = CrcKermit()
        crc_instance.process(data)
        crc_hex = crc_instance.finalbytes().hex().upper()
        crc_hex = crc_hex.zfill(4)
        # SAS requires the 2 CRC bytes to be reversed
        return command + crc_hex[2:4] + crc_hex[0:2]
    except Exception as e:
        print(f"CRC Error: {e}")
        return command + "0000"

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
    """Send data to SAS port with proper SAS parity switching"""
    global sasport
    
    if not sasport or not sasport.isOpen():
        print("❌ Serial port not available")
        return False
        
    try:
        command_hex = command_hex.replace(" ", "")
        
        if len(command_hex) < 2:
            print("❌ Command too short")
            return False
            
        # SAS Protocol: First byte with MARK parity, rest with SPACE parity
        # This matches the main app's parity switching for device type 8
        
        # Send first byte with MARK parity
        sasport.parity = serial.PARITY_MARK
        first_byte = bytes.fromhex(command_hex[0:2])
        bytes_written = sasport.write(first_byte)
        sasport.flush()
        
        print(f"🔍 Sent first byte with MARK parity: {command_hex[0:2]} ({bytes_written} bytes)")
        
        # Send rest with SPACE parity (if there are more bytes)
        if len(command_hex) > 2:
            time.sleep(0.005)  # Small delay like main app
            sasport.parity = serial.PARITY_SPACE
            rest_bytes = bytes.fromhex(command_hex[2:])
            bytes_written += sasport.write(rest_bytes)
            sasport.flush()
            
            print(f"🔍 Sent rest with SPACE parity: {command_hex[2:]} ({len(rest_bytes)} bytes)")
        
        print(f"🔍 Total bytes written: {bytes_written}")
        
        return True
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def SendSASCommand(command_hex):
    """Send SAS command - EXACTLY matching original SendSASCommand"""
    global last_sent_poll_type
    
    command_hex = command_hex.replace(" ", "")
    
    # Update last sent times like original
    if command_hex.endswith("81"):
        last_sent_poll_type = 81
    if command_hex.endswith("80"):
        last_sent_poll_type = 80

    # Log all commands with more detail
    if command_hex.endswith(("80", "81")):
        # Polling commands - show less frequently
        pass  # Will be shown in polling function
    else:
        print(f"TX: {command_hex} at {datetime.datetime.now()}")
        print(f"    Command breakdown: Address={command_hex[0:2]}, Command={command_hex[2:4]}, Length={len(command_hex)//2} bytes")
    
    # Send command
    success = SendSASPORT(command_hex)
    if not success:
        print(f"❌ Failed to send command: {command_hex}")
    
    return success

def ReadSASPORT():
    """Read response from SAS port - EXACTLY matching original"""
    global sasport
    
    if not sasport or not sasport.isOpen():
        return ""
        
    try:
        if sasport.in_waiting > 0:
            response = sasport.read(sasport.in_waiting)
            hex_response = response.hex().upper()
            # Debug: Show raw bytes received
            print(f"🔍 Raw bytes received: {len(response)} bytes -> {hex_response}")
            return hex_response
        return ""
    except Exception as e:
        print(f"❌ Read error: {e}")
        return ""

def continuous_polling():
    """Continuous SAS polling thread - EXACTLY matching original pattern"""
    global polling_active, aft_response_received, aft_transfer_status
    global balance_response_received, balance_amount
    
    print("🔄 Starting SAS polling loop...")
    
    # Polling commands
    general_poll = GetCRC(SAS_ADDRESS + "80")  # General poll
    interrogation = GetCRC(SAS_ADDRESS + "81")  # Interrogation
    
    poll_counter = 0
    last_poll_time = time.time()
    response_count = 0
    no_response_count = 0
    
    while polling_active:
        try:
            current_time = time.time()
            
            # Send poll every 200ms (alternating between general poll and interrogation)
            if current_time - last_poll_time >= 0.2:
                # Alternate between general poll (80) and interrogation (81)
                if poll_counter % 10 == 0:
                    # Every 10th poll, send interrogation
                    SendSASCommand(interrogation)
                    poll_type = "INTERROGATION"
                else:
                    # Otherwise, send general poll
                    SendSASCommand(general_poll)
                    poll_type = "GENERAL_POLL"
                
                time.sleep(0.05)  # Wait for response
                
                # Check for response
                response = ReadSASPORT()
                if response:
                    response_count += 1
                    print(f"🔍 RX[{response_count}] ({poll_type}): {response} at {datetime.datetime.now()}")
                    
                    # Handle AFT responses - EXACTLY like original
                    if len(response) >= 4 and response[0:4] == "0172":
                        print("📊 AFT Transfer Response Received!")
                        Yanit_ParaYukle(response)
                    elif len(response) >= 4 and response[0:4] == "0174":
                        print("💰 Balance Response Received!")
                        Yanit_BakiyeSorgulama(response)
                    elif response == "69":
                        print("✓ AFT completion notification received!")
                        aft_transfer_status = "00"  # Success like original
                        aft_response_received = True
                    elif response in ["01", "00"]:
                        # Normal responses - show occasionally for debugging
                        if response_count % 20 == 1:  # Every 20th response
                            print(f"🔄 Normal response: {response} (showing 1 in 20)")
                    else:
                        # Other responses - log for debugging
                        print(f"🔍 Other response: {response}")
                else:
                    no_response_count += 1
                    # Show no-response status every 50 polls
                    if poll_counter % 50 == 0:
                        print(f"⚠️  No response for {no_response_count} polls (total polls: {poll_counter})")
                
                poll_counter += 1
                last_poll_time = current_time
                
                # Debug: Show polling stats every 100 polls
                if poll_counter % 100 == 0:
                    print(f"📊 Polling Stats: {poll_counter} polls sent, {response_count} responses, {no_response_count} no-responses")
            
            time.sleep(0.01)  # Small delay to prevent CPU spinning
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
            time.sleep(0.1)
    
    print(f"🔄 Polling stopped - Final stats: {poll_counter} polls, {response_count} responses")

def Yanit_ParaYukle(response):
    """Parse AFT response - EXACTLY like original Yanit_ParaYukle"""
    global aft_transfer_status, aft_response_received
    
    try:
        print(f"📥 ========== AFT TRANSFER RESPONSE ==========")
        print(f"📥 RAW RESPONSE: {response}")
        print(f"===============================================")
        
        if len(response) < 10:
            print("Response too short")
            aft_transfer_status = "FF"
            aft_response_received = True
            return
            
        # Parse like original - extract transfer status at position 12-13
        transfer_status = response[12:14]  # Position 12-13 in response (CORRECTED)
        aft_transfer_status = transfer_status
        aft_response_received = True
        
        # Status descriptions from original
        status_descriptions = {
            "00": "Transfer successful",
            "81": "TransactionID is not unique",
            "82": "Registration key does not match",
            "83": "No POS ID or POS ID does not match",
            "84": "Transfer amount exceeds machine limit",
            "87": "Gaming machine unable to accept transfers",
            "C0": "Transfer request acknowledged/pending",
            "FF": "Transfer failed - general error"
        }
        
        status_text = status_descriptions.get(transfer_status, f"Unknown status: {transfer_status}")
        
        print(f"📊 Transfer Status: {transfer_status} - {status_text}")
        print(f"===============================================")
        
        if transfer_status == "00":
            print("✅ AFT Transfer is completed successfully!")
        elif transfer_status == "C0":
            print("⏳ AFT Transfer acknowledged, processing...")
        else:
            print(f"❌ AFT Transfer failed: {status_text}")
        
    except Exception as e:
        print(f"❌ Error parsing AFT response: {e}")
        aft_transfer_status = "FF"
        aft_response_received = True

def Yanit_BakiyeSorgulama(response):
    """Parse balance response - EXACTLY like original"""
    global balance_response_received, balance_amount
    
    try:
        print(f"💰 ========== BALANCE RESPONSE ==========")
        print(f"💰 RAW RESPONSE: {response}")
        print(f"💰 Response length: {len(response)} characters")
        print(f"===========================================")
        
        if len(response) < 40:  # Need at least 40 chars for basic balance data
            print("Response too short for balance parsing")
            balance_response_received = True
            return
        
        # Parse according to SAS 74h response format
        # Format: Address(2) + Command(2) + Length(2) + AssetNumber(8) + GameLockStatus(2) + ...
        index = 6  # Skip address, command, length
        
        asset_number = response[index:index+8] if index + 8 <= len(response) else "00000000"
        index += 8
        print(f"💰 Asset Number: {asset_number}")
        
        game_lock_status = response[index:index+2] if index + 2 <= len(response) else "00"
        index += 2
        print(f"💰 Game Lock Status: {game_lock_status}")
        
        available_transfers = response[index:index+2] if index + 2 <= len(response) else "00"
        index += 2
        print(f"💰 Available Transfers: {available_transfers}")
        
        host_cashout_status = response[index:index+2] if index + 2 <= len(response) else "00"
        index += 2
        print(f"💰 Host Cashout Status: {host_cashout_status}")
        
        aft_status = response[index:index+2] if index + 2 <= len(response) else "00"
        index += 2
        print(f"💰 AFT Status: {aft_status}")
        
        max_buffer_index = response[index:index+2] if index + 2 <= len(response) else "00"
        index += 2
        print(f"💰 Max Buffer Index: {max_buffer_index}")
        
        # Current cashable amount (5 bytes BCD = 10 hex characters)
        current_cashable_amount = response[index:index+10] if index + 10 <= len(response) else "0000000000"
        index += 10
        print(f"💰 Current Cashable Amount (raw BCD): {current_cashable_amount}")
        
        # Convert BCD to decimal (divide by 100 for cents to dollars)
        try:
            cashable_amount_raw = bcd_to_int(current_cashable_amount)
            balance_amount = cashable_amount_raw / 100
            print(f"💰 BCD conversion: '{current_cashable_amount}' -> {cashable_amount_raw} cents -> ${balance_amount}")
        except ValueError as e:
            print(f"💰 Error converting cashable amount: {e}")
            balance_amount = 0
        
        balance_response_received = True
        
        print(f"💰 Final Balance: ${balance_amount}")
        print(f"===========================================")
        
    except Exception as e:
        print(f"❌ Error parsing balance response: {e}")
        balance_response_received = True

def bcd_to_int(bcd_str):
    """Convert a BCD string to integer - EXACTLY like original"""
    digits = ''
    for i in range(0, len(bcd_str), 2):
        byte = bcd_str[i:i+2]
        if len(byte) < 2:
            continue
        high = int(byte[0], 16)
        low = int(byte[1], 16)
        digits += f"{high}{low}"
    return int(digits.lstrip('0') or '0')

def wait_for_aft_completion():
    """Wait for AFT completion - like original"""
    global aft_response_received, aft_transfer_status
    
    print("Waiting for AFT completion...")
    
    timeout = 30  # 30 seconds timeout
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if aft_response_received:
            if aft_transfer_status == "00":
                print("✅ AFT transfer completed successfully!")
                return True
            elif aft_transfer_status == "C0":
                print("⏳ AFT transfer acknowledged, continuing to wait...")
                # Reset to continue waiting for final status
                aft_response_received = False
                aft_transfer_status = None
                continue
            else:
                print(f"❌ AFT transfer failed with status: {aft_transfer_status}")
                return False
        
        time.sleep(0.1)
    
    print("❌ Timeout waiting for AFT completion")
    return False

def wait_for_balance_response():
    """Wait for balance query response"""
    global balance_response_received
    
    print("Waiting for balance response...")
    
    timeout = 10  # 10 seconds timeout
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if balance_response_received:
            print("✅ Balance response received!")
            return True
        time.sleep(0.1)
    
    print("❌ Timeout waiting for balance response")
    return False

def send_balance_query():
    """Send balance query command (SAS 74h)"""
    print("💰 Sending balance query...")
    
    # Balance query command - unlocked format
    balance_command = GetCRC(SAS_ADDRESS + "7400000000")
    print(f"💰 Balance command: {balance_command}")
    
    SendSASCommand(balance_command)
    return True

def test_serial_connectivity():
    """Test basic serial port connectivity"""
    global sasport
    
    print("\n🔧 Testing Serial Port Connectivity...")
    print(f"Port: {sasport.port}")
    print(f"Baudrate: {sasport.baudrate}")
    print(f"Bytesize: {sasport.bytesize}")
    print(f"Parity: {sasport.parity}")
    print(f"Stopbits: {sasport.stopbits}")
    print(f"Timeout: {sasport.timeout}")
    print(f"DTR: {sasport.dtr}")
    print(f"RTS: {sasport.rts}")
    print(f"DSR: {sasport.dsr}")
    print(f"CTS: {sasport.cts}")
    print(f"CD: {sasport.cd}")
    print(f"RI: {sasport.ri}")
    
    # Test basic poll
    print("\n🔧 Sending test poll...")
    test_poll = GetCRC(SAS_ADDRESS + "80")
    print(f"Test poll command: {test_poll}")
    
    success = SendSASPORT(test_poll)
    if success:
        print("✓ Test poll sent successfully")
        
        # Wait for response
        time.sleep(0.1)
        response = ReadSASPORT()
        if response:
            print(f"✓ Got response: {response}")
            return True
        else:
            print("❌ No response to test poll")
            
            # Check if there's any data waiting
            if sasport.in_waiting > 0:
                print(f"⚠️  {sasport.in_waiting} bytes waiting in buffer")
                raw_data = sasport.read(sasport.in_waiting)
                print(f"Raw buffer data: {raw_data.hex().upper()}")
            else:
                print("📭 No data in receive buffer")
            return False
    else:
        print("❌ Failed to send test poll")
        return False

def main():
    """Main function"""
    global polling_active, sasport, aft_response_received, aft_transfer_status
    global balance_response_received, balance_amount
    
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 test_aft_op.py <amount>")
        print("Example: python3 test_aft_op.py 100.50")
        return 1
    
    try:
        amount = float(sys.argv[1])
        print(f"Amount to load: {amount}")
    except ValueError:
        print("❌ Invalid amount. Please enter a valid number.")
        return 1
    
    # Open SAS port
    print(f"Opening SAS port: {SAS_PORT} at {SAS_BAUDRATE} baud...")
    try:
        sasport = serial.Serial(
            port=SAS_PORT,
            baudrate=SAS_BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,  # Short timeout for polling
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        # Set DTR/RTS like original
        sasport.dtr = True
        sasport.rts = False
        
        print("✓ SAS port opened successfully")
        
        # Test connectivity first
        connectivity_ok = test_serial_connectivity()
        if not connectivity_ok:
            print("⚠️  Serial connectivity test failed - continuing anyway...")
        
    except Exception as e:
        print(f"❌ Failed to open SAS port: {e}")
        return 1
    
    try:
        # Step 1: Start continuous polling
        print("\n--- Step 1: Start SAS Polling ---")
        polling_active = True
        poll_thread = threading.Thread(target=continuous_polling, daemon=True)
        poll_thread.start()
        
        # Wait a moment for polling to start
        time.sleep(2)
        
        # Step 2: Send AFT Credit Command
        print("\n--- Step 2: Send AFT Credit Command ---")
        print(f"Building AFT command for amount: {amount}")
        
        # Convert amount to cents
        amount_cents = int(amount * 100)
        print(f"Amount in cents: {amount_cents}")
        
        # Build AFT command - EXACTLY like reference implementation
        command = "00"  # Transfer Code
        command += "00"  # Transfer Index
        command += "00"  # Transfer Type (cashable)
        
        # Amount in proper BCD format (5 bytes = 10 hex chars) - FIXED!
        cashable_amount_bcd = AddLeftBCD(amount_cents, 5)
        restricted_amount_bcd = AddLeftBCD(0, 5)  # No restricted amount
        nonrestricted_amount_bcd = AddLeftBCD(0, 5)  # No non-restricted amount
        
        command += cashable_amount_bcd  # Cashable amount (proper BCD)
        command += restricted_amount_bcd  # Restricted amount (proper BCD)
        command += nonrestricted_amount_bcd  # Non-restricted amount (proper BCD)
        
        print(f"💰 Amount breakdown:")
        print(f"   Cashable: {amount_cents} cents -> BCD: {cashable_amount_bcd}")
        print(f"   Restricted: 0 cents -> BCD: {restricted_amount_bcd}")
        print(f"   Non-restricted: 0 cents -> BCD: {nonrestricted_amount_bcd}")
        
        command += "07"  # Transfer flag (hard cashout)
        command += ASSET_NUMBER  # Asset number
        command += REGISTRATION_KEY  # Registration key
        
        # Transaction ID - EXACTLY like main app (line 740-742)
        transaction_id_int = get_next_transaction_id()  # Get integer transaction ID
        transaction_id_str = str(transaction_id_int)  # Convert to string
        print(f"💳 Transaction ID: {transaction_id_int} -> '{transaction_id_str}'")
        
        # Convert each character to hex (ASCII encoding) - EXACTLY like main app
        transaction_id_hex = "".join("{:02x}".format(ord(c)) for c in transaction_id_str)
        print(f"💳 Transaction ID hex: {transaction_id_hex}")
        
        # Transaction ID length in BCD format
        transaction_id_length_bcd = AddLeftBCD(len(transaction_id_hex)//2, 1)
        print(f"💳 Transaction ID length BCD: {transaction_id_length_bcd}")
        
        command += transaction_id_length_bcd  # Transaction ID length (BCD)
        command += transaction_id_hex  # Transaction ID (hex encoded ASCII)
        
        command += "00000000"  # Expiration date
        command += "0000"  # Pool ID
        command += "00"  # Receipt data length
        
        # Build header
        command_header = SAS_ADDRESS + "72"  # Address + Command
        command_header += f"{len(command)//2:02X}"  # Length
        
        # Final command
        full_command = GetCRC(command_header + command)
        
        print(f"\n🔧 AFT Command Analysis:")
        print(f"   Header: {command_header}")
        print(f"   Body: {command}")
        print(f"   Full command: {full_command}")
        print(f"   Command length: {len(full_command)} hex chars ({len(full_command)//2} bytes)")
        
        # Validate command structure
        if len(full_command) < 10:
            print("❌ Command too short!")
            return 1
            
        expected_length = int(command_header[4:6], 16) + 5  # Header + CRC
        actual_length = len(full_command) // 2
        if actual_length != expected_length:
            print(f"⚠️  Length mismatch: Expected {expected_length}, got {actual_length}")
        
        # Reset AFT response flags
        aft_response_received = False
        aft_transfer_status = None
        
        print(f"\n📤 Sending AFT Credit Load Command...")
        success = SendSASCommand(full_command)
        if not success:
            print("❌ Failed to send AFT command")
            return 1
        
        # Step 3: Wait for AFT completion
        print("\n--- Step 3: Wait for AFT Completion ---")
        aft_success = wait_for_aft_completion()
        
        if aft_success:
            print("✅ AFT operation completed successfully!")
            
            # Step 4: Query balance to verify credit was applied
            print("\n--- Step 4: Verify Balance ---")
            print("Waiting a moment for machine to process credit...")
            time.sleep(2)  # Give machine time to process
            
            # Reset balance response flags
            balance_response_received = False
            balance_amount = 0.0
            
            # Send balance query
            if send_balance_query():
                if wait_for_balance_response():
                    print(f"✅ Current balance: ${balance_amount}")
                    if balance_amount >= amount:
                        print(f"✅ SUCCESS: Balance increased by at least ${amount}!")
                    elif balance_amount > 0:
                        print(f"⚠️  PARTIAL: Balance is ${balance_amount}, expected at least ${amount}")
                    else:
                        print(f"❌ ISSUE: Balance is still ${balance_amount}, credit may not have been applied")
                else:
                    print("❌ Failed to get balance response")
            else:
                print("❌ Failed to send balance query")
        else:
            print("❌ AFT operation failed or timed out")
        
        # Step 5: Stop polling and cleanup
        print("\n--- Step 5: Cleanup ---")
        polling_active = False
        time.sleep(1)  # Wait for polling thread to stop
        
    finally:
        # Close serial port
        if sasport and sasport.is_open:
            sasport.close()
            print("✓ SAS port closed")
    
    print("\nAFT test completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
