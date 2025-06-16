#!/usr/bin/env python3
"""
AFT Registration Discovery Tool
This script uses the existing working SAS functions to discover the current AFT registration key.
"""

import sys
import time
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from sas_money_functions import SasMoney
from port_manager import PortManager
from sas_communicator import SASCommunicator

class AFTRegistrationDiscovery:
    """Tool to discover current AFT registration settings using existing working functions"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.port_mgr = PortManager()
        self.sas_comm = None
        self.sas_money = None
        
    def initialize_sas(self):
        """Initialize SAS communication using the working SasMoney class"""
        try:
            print("🔍 AFT Registration Discovery Tool")
            print("This tool will query the machine to discover current AFT registration settings.")
            print("Using existing working SAS functions...")
            print()
            
            # Find and connect to SAS port first
            print("Finding SAS port...")
            port_info = self.port_mgr.find_sas_port(self.config)
            
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
            
            # Initialize SAS money functions with the communicator
            self.sas_money = SasMoney(self.config, self.sas_comm)
            
            if not self.sas_money:
                print("❌ Failed to initialize SAS money functions!")
                return False
                
            print("✅ SAS communication initialized using working functions")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing SAS: {e}")
            return False
    
    def discover_registration_key_method1(self):
        """Method 1: Try to read registration key from config files"""
        try:
            print("\n🔍 Method 1: Checking Configuration Files...")
            
            # Check settings.ini
            try:
                import configparser
                settings_config = configparser.ConfigParser()
                settings_config.read('settings.ini')
                
                if 'DEFAULT' in settings_config and 'registrationkey' in settings_config['DEFAULT']:
                    settings_key = settings_config['DEFAULT']['registrationkey']
                    print(f"📄 settings.ini registration key: {settings_key}")
                    
                    if settings_key == "0" * 40:
                        print("   📝 Type: All zeros (default/empty key)")
                    else:
                        print("   📝 Type: Custom registration key")
                else:
                    print("   ⚠️  No registration key found in settings.ini")
                    
            except Exception as e:
                print(f"   ❌ Error reading settings.ini: {e}")
            
            # Check config.ini
            try:
                config_config = configparser.ConfigParser()
                config_config.read('config.ini')
                
                if 'DEFAULT' in config_config and 'registrationkey' in config_config['DEFAULT']:
                    config_key = config_config['DEFAULT']['registrationkey']
                    print(f"📄 config.ini registration key: {config_key}")
                    
                    if config_key == "0" * 40:
                        print("   📝 Type: All zeros (default/empty key)")
                    else:
                        print("   📝 Type: Custom registration key")
                else:
                    print("   ⚠️  No registration key found in config.ini")
                    
            except Exception as e:
                print(f"   ❌ Error reading config.ini: {e}")
                
        except Exception as e:
            print(f"❌ Error in method 1: {e}")
    
    def discover_registration_key_method2(self):
        """Method 2: Try AFT registration with different keys to see which one works"""
        try:
            print("\n🔍 Method 2: Testing Registration Keys...")
            
            # Test keys to try
            test_keys = [
                ("0000000000000000000000000000000000000000", "All zeros (original working key)"),
                ("1234567890ABCDEF1234567890ABCDEF12345678", "Test pattern from config.ini"),
                ("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", "All F's"),
                ("1111111111111111111111111111111111111111", "All 1's")
            ]
            
            for key, description in test_keys:
                print(f"\n🧪 Testing: {description}")
                print(f"   Key: {key}")
                
                try:
                    # Try AFT registration with this key
                    result = self.sas_money.komut_aft_registration(
                        asset_number="0000006C",  # Known asset number
                        registration_key=key,
                        pos_id="TEST01"
                    )
                    
                    print(f"   Result: {result}")
                    
                    if result:
                        print(f"   ✅ SUCCESS! This key works: {key}")
                        print(f"   📝 Description: {description}")
                        
                        # Save successful key
                        with open("working_registration_key.txt", "w") as f:
                            f.write(f"Working AFT Registration Key: {key}\n")
                            f.write(f"Description: {description}\n")
                            f.write(f"Discovery Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        print("   💾 Working key saved to 'working_registration_key.txt'")
                        return key
                    else:
                        print(f"   ❌ Failed with this key")
                        
                except Exception as e:
                    print(f"   ❌ Error testing key: {e}")
                
                # Wait between tests
                time.sleep(1)
            
            print("\n⚠️  No working registration key found in test set")
            return None
            
        except Exception as e:
            print(f"❌ Error in method 2: {e}")
            return None
    
    def discover_registration_key_method3(self):
        """Method 3: Try to clear registration and see what happens"""
        try:
            print("\n🔍 Method 3: Testing Registration Clear/Reset...")
            
            # Try to clear AFT registration
            print("Attempting to clear AFT registration...")
            clear_result = self.sas_money.komut_aft_clear_registration()
            print(f"Clear registration result: {clear_result}")
            
            # Try to cancel any pending transfers
            print("Attempting to cancel AFT transfers...")
            cancel_result = self.sas_money.komut_cancel_aft_transfer()
            print(f"Cancel transfer result: {cancel_result}")
            
            # Now try to register with all zeros (most common default)
            print("Attempting registration with all-zeros key...")
            register_result = self.sas_money.komut_aft_registration(
                asset_number="0000006C",
                registration_key="0000000000000000000000000000000000000000",
                pos_id="TEST01"
            )
            print(f"Registration with zeros result: {register_result}")
            
            if register_result:
                print("✅ SUCCESS! All-zeros key works after clearing registration")
                return "0000000000000000000000000000000000000000"
            else:
                print("❌ All-zeros key still doesn't work after clearing")
                return None
                
        except Exception as e:
            print(f"❌ Error in method 3: {e}")
            return None
    
    def run_discovery(self):
        """Run the complete AFT registration discovery process"""
        try:
            if not self.initialize_sas():
                return False
            
            print("\n" + "="*60)
            print("🔍 STARTING AFT REGISTRATION KEY DISCOVERY")
            print("="*60)
            
            # Method 1: Check config files
            self.discover_registration_key_method1()
            
            # Method 2: Test different keys
            working_key = self.discover_registration_key_method2()
            
            if working_key:
                print(f"\n🎉 DISCOVERY SUCCESSFUL!")
                print(f"Working registration key: {working_key}")
            else:
                # Method 3: Try clearing and resetting
                working_key = self.discover_registration_key_method3()
                
                if working_key:
                    print(f"\n🎉 DISCOVERY SUCCESSFUL AFTER RESET!")
                    print(f"Working registration key: {working_key}")
                else:
                    print(f"\n❌ DISCOVERY FAILED")
                    print("Could not find a working registration key.")
                    print("The machine may need to be reset or have AFT disabled.")
            
            print("\n" + "="*60)
            print("✅ AFT REGISTRATION KEY DISCOVERY COMPLETE")
            print("="*60)
            
            return working_key is not None
            
        except Exception as e:
            print(f"❌ Error in discovery process: {e}")
            return False

if __name__ == "__main__":
    discovery = AFTRegistrationDiscovery()
    discovery.run_discovery() 