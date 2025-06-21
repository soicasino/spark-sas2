#!/usr/bin/env python3
"""
Test script to verify the netifaces replacement works
"""

import sys
import traceback

def test_imports():
    """Test that all imports work"""
    try:
        print("Testing imports...")
        from utils import get_mac_address, get_ip_address
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_mac_address():
    """Test MAC address function"""
    try:
        print("\nTesting MAC address function...")
        from utils import get_mac_address
        
        # Test with default interface
        mac = get_mac_address()
        print(f"Default interface MAC: {mac}")
        
        # Test with common interfaces
        for interface in ['eth0', 'wlan0', 'lo']:
            mac = get_mac_address(interface)
            print(f"Interface {interface} MAC: {mac}")
        
        print("✅ MAC address function works")
        return True
    except Exception as e:
        print(f"❌ MAC address test failed: {e}")
        traceback.print_exc()
        return False

def test_ip_address():
    """Test IP address function"""
    try:
        print("\nTesting IP address function...")
        from utils import get_ip_address
        
        ip = get_ip_address()
        print(f"IP address: {ip}")
        
        print("✅ IP address function works")
        return True
    except Exception as e:
        print(f"❌ IP address test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing netifaces replacement fix...\n")
    
    success = True
    success &= test_imports()
    success &= test_mac_address()
    success &= test_ip_address()
    
    if success:
        print("\n🎉 All tests passed! The netifaces fix is working.")
        print("You can now run: python main.py")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 