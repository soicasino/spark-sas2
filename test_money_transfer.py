#!/usr/bin/env python3
"""
Test script for money transfer functionality
Tests the new wait-for-completion logic
"""

import asyncio
import time
from datetime import datetime
from sas_money_functions import SasMoney

class MockCommunicator:
    """Mock communicator for testing"""
    def __init__(self):
        self.sent_commands = []
        self.simulate_success = True
        self.response_delay = 1.0  # Simulate 1 second response time
        
    def sas_send_command_with_queue(self, command_name, command, priority):
        """Mock command sending"""
        print(f"MOCK: Sending {command_name}: {command}")
        self.sent_commands.append((command_name, command, priority))
        
        # Simulate async response after delay
        if command_name in ["ParaYukle", "Cashout"]:
            asyncio.create_task(self._simulate_response(command_name))
    
    async def _simulate_response(self, command_name):
        """Simulate machine response after delay"""
        await asyncio.sleep(self.response_delay)
        
        # Simulate response by calling the response handler
        if hasattr(self, 'sas_money'):
            if command_name == "ParaYukle":
                # Simulate successful transfer response
                status = "00" if self.simulate_success else "84"
                self.sas_money.global_para_yukleme_transfer_status = status
                print(f"MOCK: Simulated ParaYukle response: {status}")
            elif command_name == "Cashout":
                # Simulate successful cashout response
                status = "00" if self.simulate_success else "87"
                self.sas_money.global_para_silme_transfer_status = status
                print(f"MOCK: Simulated Cashout response: {status}")

class MockConfig:
    """Mock configuration"""
    def get(self, section, key):
        return "8"  # Default casino ID

async def test_money_transfer():
    """Test the money transfer functionality"""
    print("=== Testing Money Transfer Functionality ===\n")
    
    # Setup
    config = MockConfig()
    communicator = MockCommunicator()
    sas_money = SasMoney(config, communicator)
    communicator.sas_money = sas_money  # Link for response simulation
    
    # Test 1: Successful money load
    print("Test 1: Money Load (Success)")
    print("-" * 30)
    
    start_time = time.time()
    transaction_id = sas_money.komut_para_yukle(
        doincreasetransactionid=1,
        transfertype=10,  # Cashable
        customerbalance=25.00,
        customerpromo=0.0,
        transactionid=1001,
        assetnumber="0000006C",
        registrationkey="00000000000000000000000000000000000000000000"
    )
    
    print(f"Command sent, transaction ID: {transaction_id}")
    print("Waiting for completion...")
    
    result = await sas_money.wait_for_para_yukle_completion(timeout=5)
    elapsed = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Status: {sas_money.global_para_yukleme_transfer_status}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Expected: True (success)")
    print(f"✅ PASS" if result is True else f"❌ FAIL")
    print()
    
    # Test 2: Failed money load
    print("Test 2: Money Load (Failure)")
    print("-" * 30)
    
    communicator.simulate_success = False
    
    start_time = time.time()
    transaction_id = sas_money.komut_para_yukle(
        doincreasetransactionid=1,
        transfertype=10,
        customerbalance=1000.00,  # Large amount to trigger failure
        customerpromo=0.0,
        transactionid=1002,
        assetnumber="0000006C",
        registrationkey="00000000000000000000000000000000000000000000"
    )
    
    print(f"Command sent, transaction ID: {transaction_id}")
    print("Waiting for completion...")
    
    result = await sas_money.wait_for_para_yukle_completion(timeout=5)
    elapsed = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Status: {sas_money.global_para_yukleme_transfer_status}")
    print(f"Status description: {sas_money.get_transfer_status_description(sas_money.global_para_yukleme_transfer_status)}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Expected: False (failure)")
    print(f"✅ PASS" if result is False else f"❌ FAIL")
    print()
    
    # Test 3: Timeout
    print("Test 3: Money Load (Timeout)")
    print("-" * 30)
    
    communicator.response_delay = 10.0  # Long delay to trigger timeout
    
    start_time = time.time()
    transaction_id = sas_money.komut_para_yukle(
        doincreasetransactionid=1,
        transfertype=10,
        customerbalance=50.00,
        customerpromo=0.0,
        transactionid=1003,
        assetnumber="0000006C",
        registrationkey="00000000000000000000000000000000000000000000"
    )
    
    print(f"Command sent, transaction ID: {transaction_id}")
    print("Waiting for completion (should timeout)...")
    
    result = await sas_money.wait_for_para_yukle_completion(timeout=2)
    elapsed = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Status: {sas_money.global_para_yukleme_transfer_status}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Expected: None (timeout)")
    print(f"✅ PASS" if result is None else f"❌ FAIL")
    print()
    
    # Test 4: Cashout
    print("Test 4: Cashout (Success)")
    print("-" * 30)
    
    communicator.simulate_success = True
    communicator.response_delay = 1.0
    
    # Set some balance to cashout
    sas_money.yanit_bakiye_tutar = 75.50
    sas_money.yanit_restricted_amount = 10.25
    sas_money.yanit_nonrestricted_amount = 5.00
    
    start_time = time.time()
    transaction_id = sas_money.komut_para_sifirla(
        doincreaseid=1,
        transactionid=2001,
        assetnumber="0000006C",
        registrationkey="00000000000000000000000000000000000000000000"
    )
    
    print(f"Command sent, transaction ID: {transaction_id}")
    print(f"Cashout amounts: ${sas_money.yanit_bakiye_tutar}, ${sas_money.yanit_restricted_amount}, ${sas_money.yanit_nonrestricted_amount}")
    print("Waiting for completion...")
    
    result = await sas_money.wait_for_para_sifirla_completion(timeout=5)
    elapsed = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Status: {sas_money.global_para_silme_transfer_status}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Expected: True (success)")
    print(f"✅ PASS" if result is True else f"❌ FAIL")
    print()
    
    print("=== Test Summary ===")
    print("Commands sent:", len(communicator.sent_commands))
    for i, (name, cmd, priority) in enumerate(communicator.sent_commands, 1):
        print(f"{i}. {name} (priority {priority}): {cmd[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_money_transfer()) 