#!/usr/bin/env python3
"""
Test script to verify the fixed meter parsing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sas_money_functions import SasMoney
from config_manager import ConfigManager

# Mock communicator for testing
class MockCommunicator:
    def sas_send_command_with_queue(self, command_type, command, priority):
        pass

def test_meter_parsing():
    """Test the meter parsing with the actual response data"""
    
    # Initialize config and SAS money
    config = ConfigManager()
    communicator = MockCommunicator()
    sas_money = SasMoney(config, communicator)
    
    # Test data from the logs
    test_data = "01AF880000A00009000000000089475290B800090000000000903522900200090000000000000000000300090000000000000000001E00090000000000000000000000090000000000131870000100090000000000129982000B0009000000000000276500A20009000000000000000000BA0009000000000000000000050004000103350600040000149840CD"
    
    print("=== Testing Meter Parsing ===")
    print(f"Test data length: {len(test_data)} chars")
    
    # Call the meter parsing function directly
    result = sas_money.handle_single_meter_response(test_data)
    
    print(f"Parsing result: {result}")
    print(f"Last parsed meters: {sas_money.last_parsed_meters}")
    
    # Check if the meters were stored correctly
    if hasattr(sas_money, 'last_parsed_meters') and sas_money.last_parsed_meters:
        print("✅ SUCCESS: Meters were parsed and stored successfully!")
        
        print("\n=== Parsed Meter Summary ===")
        for meter_name, value in sas_money.last_parsed_meters.items():
            if 'games' in meter_name.lower():
                print(f"  {meter_name}: {value} games")
            else:
                print(f"  {meter_name}: {value:,.2f} TL")
    else:
        print("❌ FAILED: No meters were parsed or stored")
        
    return sas_money.last_parsed_meters

if __name__ == "__main__":
    test_meter_parsing() 