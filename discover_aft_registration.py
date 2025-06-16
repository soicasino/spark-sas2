#!/usr/bin/env python3
"""
AFT Registration Discovery Tool
This script queries the machine to discover the current AFT registration key and settings.
"""

import sys
import time
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from port_manager import PortManager
from sas_communicator import SASCommunicator

class AFTRegistrationDiscovery:
    """Tool to discover current AFT registration settings"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.port_mgr = PortManager()
        self.sas_comm = None
        self.running = False
        self.sas_poll_timer = None
        
    def initialize_sas(self):
        """Initialize SAS communication with proper polling"""
        try:
            print("🔍 AFT Registration Discovery Tool")
            print("This tool will query the machine to discover current AFT registration settings.")
            print()
            
            # Find and connect to SAS port
            print("Finding SAS port...")
            port_info = self.port_mgr.find_sas_port()
            
            if not port_info:
                print("❌ No SAS port found!")
                return False
                
            port_name, device_type = port_info
            print(f"✅ Found SAS on port: {port_name}, device type: {device_type}")
            
            # Initialize SAS communicator
            self.sas_comm = SASCommunicator(
                port_name=port_name,
                global_config=self.config
            )
            
            # Start polling to keep machine responsive
            print("Starting SAS polling...")
            self.running = True
            self.start_polling()
            
            # Wait for initial communication
            time.sleep(2)
            
            print("✅ SAS communication initialized")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing SAS: {e}")
            return False
    
    def start_polling(self):
        """Start the SAS polling loop"""
        if self.running and self.sas_comm:
            try:
                # Send general poll
                self.sas_comm.sas_send_command_with_queue("GeneralPoll", "01800039", 0)
                
                # Schedule next poll
                import threading
                self.sas_poll_timer = threading.Timer(0.04, self.start_polling)  # 40ms
                self.sas_poll_timer.daemon = True
                self.sas_poll_timer.start()
                
            except Exception as e:
                print(f"Polling error: {e}")
    
    def stop_polling(self):
        """Stop the SAS polling loop"""
        self.running = False
        if self.sas_poll_timer:
            self.sas_poll_timer.cancel()
    
    def query_aft_registration_status(self):
        """Query current AFT registration status using SAS 73h FF command"""
        try:
            print("\n🔍 Querying AFT Registration Status...")
            
            # Build AFT registration status query command
            # Format: Address + Command + Length + Status Code
            sas_address = "01"
            command_code = "73"
            command_length = "01"  # 1 byte for status code
            status_code = "FF"     # FF = Query current registration status
            
            # Build complete command
            command_no_crc = sas_address + command_code + command_length + status_code
            
            # Add CRC
            from crccheck.crc import CrcKermit
            data = bytearray.fromhex(command_no_crc)
            crc_instance = CrcKermit()
            crc_instance.process(data)
            crc_bytes = crc_instance.finalbytes()
            crc_hex = crc_bytes.hex().upper().zfill(4)
            complete_command = command_no_crc + crc_hex[2:4] + crc_hex[0:2]
            
            print(f"Sending AFT registration query: {complete_command}")
            
            # Send the command
            result = self.sas_comm.sas_send_command_with_queue("AFTRegQuery", complete_command, 1)
            print(f"Command result: {result}")
            
            # Wait for response
            time.sleep(2)
            
            # Check if we got a response in the SAS buffer
            if hasattr(self.sas_comm, 'last_received_data'):
                response = getattr(self.sas_comm, 'last_received_data', None)
                if response:
                    print(f"Raw response: {response}")
                    self.parse_aft_registration_response(response)
                else:
                    print("⚠️  No response received")
            else:
                print("⚠️  No response mechanism available")
                
            return result
            
        except Exception as e:
            print(f"❌ Error querying AFT registration: {e}")
            return None
    
    def parse_aft_registration_response(self, response):
        """Parse AFT registration response to extract registration key and settings"""
        try:
            print(f"\n📋 Parsing AFT Registration Response:")
            print(f"Raw response: {response}")
            print(f"Response length: {len(response)} characters")
            
            if len(response) < 6:
                print("❌ Response too short")
                return
            
            # Parse response structure
            index = 0
            address = response[index:index+2]
            index += 2
            print(f"Address: {address}")
            
            command = response[index:index+2]
            index += 2
            print(f"Command: {command}")
            
            if command.upper() != "73":
                print(f"❌ Unexpected command: {command}, expected 73")
                return
            
            length_hex = response[index:index+2]
            index += 2
            print(f"Length: {length_hex}")
            
            try:
                length = int(length_hex, 16)
                print(f"Parsed length: {length} bytes")
            except ValueError:
                print(f"❌ Invalid length: {length_hex}")
                return
            
            # Check if we have enough data
            expected_total = 6 + (length * 2)
            if len(response) < expected_total:
                print(f"⚠️  Incomplete response: got {len(response)}, expected {expected_total}")
            
            # Parse registration data
            if length >= 1:
                registration_status = response[index:index+2]
                index += 2
                print(f"Registration Status: {registration_status}")
                
                if registration_status == "00":
                    print("✅ Machine is registered for AFT")
                elif registration_status == "80":
                    print("❌ Machine is NOT registered for AFT")
                    return
                else:
                    print(f"⚠️  Unknown registration status: {registration_status}")
            
            if length >= 5:  # Asset number (4 bytes)
                asset_number = response[index:index+8]
                index += 8
                print(f"Asset Number: {asset_number}")
                
                # Convert to decimal
                try:
                    asset_decimal = int(asset_number, 16)
                    print(f"Asset Number (decimal): {asset_decimal}")
                except:
                    pass
            
            if length >= 25:  # Registration key (20 bytes = 40 hex chars)
                registration_key = response[index:index+40]
                index += 40
                print(f"🔑 Registration Key: {registration_key}")
                
                # Check if it's all zeros
                if registration_key == "0" * 40:
                    print("   📝 Key Type: All zeros (default/empty key)")
                else:
                    print("   📝 Key Type: Custom registration key")
                    
                # Save to file for reference
                with open("discovered_registration_key.txt", "w") as f:
                    f.write(f"Discovered AFT Registration Key: {registration_key}\n")
                    f.write(f"Asset Number: {asset_number}\n")
                    f.write(f"Discovery Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                print("   💾 Registration key saved to 'discovered_registration_key.txt'")
            
            # Parse POS ID if available
            remaining_length = length - 25  # Subtract status(1) + asset(4) + key(20)
            if remaining_length > 0 and index < len(response):
                pos_id_hex = response[index:index+(remaining_length*2)]
                print(f"POS ID (hex): {pos_id_hex}")
                
                # Try to convert to ASCII
                try:
                    pos_id_ascii = bytes.fromhex(pos_id_hex).decode('ascii')
                    print(f"POS ID (ASCII): {pos_id_ascii}")
                except:
                    print("POS ID: (not ASCII)")
            
        except Exception as e:
            print(f"❌ Error parsing registration response: {e}")
    
    def discover_registration_from_balance_query(self):
        """Alternative method: Try to extract registration info from balance queries"""
        try:
            print("\n🔍 Alternative Method: Checking via Balance Query...")
            
            # Send balance query to see current AFT status
            asset_number = "0000006C"  # Use known asset number
            sas_address = "01"
            command = f"{sas_address}74{asset_number}"
            
            # Add CRC
            from crccheck.crc import CrcKermit
            data = bytearray.fromhex(command)
            crc_instance = CrcKermit()
            crc_instance.process(data)
            crc_bytes = crc_instance.finalbytes()
            crc_hex = crc_bytes.hex().upper().zfill(4)
            complete_command = command + crc_hex[2:4] + crc_hex[0:2]
            
            print(f"Sending balance query: {complete_command}")
            result = self.sas_comm.sas_send_command_with_queue("BalanceQuery", complete_command, 1)
            
            time.sleep(2)
            print("Balance query sent - check AFT status in response")
            
        except Exception as e:
            print(f"❌ Error in balance query method: {e}")
    
    def run_discovery(self):
        """Run the complete AFT registration discovery process"""
        try:
            if not self.initialize_sas():
                return False
            
            print("\n" + "="*60)
            print("🔍 STARTING AFT REGISTRATION DISCOVERY")
            print("="*60)
            
            # Method 1: Direct AFT registration query
            self.query_aft_registration_status()
            
            # Method 2: Balance query for additional info
            self.discover_registration_from_balance_query()
            
            print("\n" + "="*60)
            print("✅ AFT REGISTRATION DISCOVERY COMPLETE")
            print("="*60)
            
            # Keep polling for a bit to catch any delayed responses
            print("\nWaiting for any delayed responses...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in discovery process: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop_polling()
            if self.sas_comm:
                self.sas_comm.close()
        except:
            pass

if __name__ == "__main__":
    discovery = AFTRegistrationDiscovery()
    discovery.run_discovery() 