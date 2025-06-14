#!/usr/bin/env python3
"""
Test script to verify machine unlock functionality
"""

import asyncio
import time
from configparser import ConfigParser
from sas_communicator import SASCommunicator

class MockConfig:
    """Mock config for testing"""
    def __init__(self):
        self.data = {
            'sas': {'address': '01'},
            'machine': {'devicetypeid': '8'},
            'casino': {'casinoid': '8'}
        }
    
    def get(self, section, key, fallback=None):
        return self.data.get(section, {}).get(key, fallback)
    
    def getint(self, section, key, fallback=None):
        value = self.get(section, key, fallback)
        return int(value) if value is not None else fallback

async def test_machine_unlock():
    """Test machine unlock functionality"""
    print("Testing Machine Unlock Functionality")
    print("=" * 50)
    
    # Initialize communicator with proper config
    config = MockConfig()
    
    # Create a mock global config that matches what SASCommunicator expects
    global_config = {
        'sas_address': '01',
        'device_type_id': 8,
        'casino_id': 8
    }
    
    try:
        communicator = SASCommunicator(config, global_config)
    except Exception as e:
        print(f"❌ Failed to initialize SASCommunicator: {e}")
        print("This test requires a running SAS system. Try testing with the main application instead.")
        return
    
    if not hasattr(communicator, 'sas_money') or not communicator.sas_money:
        print("❌ SAS money functions not available")
        return
    
    sas_money = communicator.sas_money
    
    print("1. Checking current machine status...")
    try:
        # Query current balance/status
        sas_money.komut_bakiye_sorgulama("test", False, "status_check")
        await asyncio.sleep(2)  # Wait for response
        print("✅ Status query sent")
    except Exception as e:
        print(f"❌ Status query failed: {e}")
    
    print("\n2. Attempting to unlock machine...")
    try:
        unlock_result = sas_money.komut_unlock_machine()
        print(f"✅ Unlock command sent, result: {unlock_result}")
        await asyncio.sleep(1)  # Wait for unlock to take effect
    except Exception as e:
        print(f"❌ Unlock failed: {e}")
    
    print("\n3. Checking status after unlock...")
    try:
        # Query balance again to see if status changed
        sas_money.komut_bakiye_sorgulama("test", False, "post_unlock_check")
        await asyncio.sleep(2)  # Wait for response
        print("✅ Post-unlock status query sent")
    except Exception as e:
        print(f"❌ Post-unlock status query failed: {e}")
    
    print("\n4. Testing small AFT transfer...")
    try:
        # Try a small test transfer
        transaction_id = sas_money.komut_para_yukle(
            doincreasetransactionid=1,
            transfertype=10,  # Cashable
            customerbalance=1.0,  # $1.00 test
            customerpromo=0.0,
            transactionid=9999,
            assetnumber="0000006c",
            registrationkey="00000000000000000000000000000000000000000000"
        )
        print(f"✅ Test transfer sent, transaction ID: {transaction_id}")
        
        # Wait for completion
        result = await sas_money.wait_for_para_yukle_completion(timeout=10)
        if result is True:
            print("✅ Test transfer completed successfully!")
        elif result is False:
            print("❌ Test transfer failed")
        else:
            print("⚠️ Test transfer timed out")
            
    except Exception as e:
        print(f"❌ Test transfer failed: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_machine_unlock()) 