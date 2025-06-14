#!/usr/bin/env python3
"""
Debug script to decode and analyze AFT commands.
This script helps understand the structure of AFT commands being sent.
"""

def decode_aft_command(command_hex):
    """Decode an AFT command hex string"""
    print(f"=== AFT Command Analysis ===")
    print(f"Full command: {command_hex}")
    print(f"Length: {len(command_hex)} characters ({len(command_hex)//2} bytes)")
    
    if len(command_hex) < 10:
        print("Command too short to analyze")
        return
    
    index = 0
    
    # Address (1 byte)
    address = command_hex[index:index+2]
    index += 2
    print(f"Address: {address}")
    
    # Command (1 byte)
    command = command_hex[index:index+2]
    index += 2
    print(f"Command: {command}")
    
    # Length (1 byte)
    length_hex = command_hex[index:index+2]
    index += 2
    try:
        length = int(length_hex, 16)
        print(f"Length: {length_hex} ({length} bytes)")
    except ValueError:
        print(f"Invalid length: {length_hex}")
        return
    
    # Transfer Code (1 byte)
    transfer_code = command_hex[index:index+2]
    index += 2
    print(f"Transfer Code: {transfer_code}")
    
    # Transfer Index (1 byte)
    transfer_index = command_hex[index:index+2]
    index += 2
    print(f"Transfer Index: {transfer_index}")
    
    # Transfer Type (1 byte)
    transfer_type = command_hex[index:index+2]
    index += 2
    transfer_type_names = {
        "00": "Non-restricted",
        "10": "Cashable",
        "11": "Restricted",
        "80": "Cashout (all)",
        "90": "Cashout (partial)"
    }
    print(f"Transfer Type: {transfer_type} ({transfer_type_names.get(transfer_type, 'Unknown')})")
    
    # Cashable Amount (5 bytes BCD)
    cashable_amount = command_hex[index:index+10]
    index += 10
    try:
        cashable_cents = int(cashable_amount, 16)
        cashable_dollars = cashable_cents / 100
        print(f"Cashable Amount: {cashable_amount} ({cashable_cents} cents = ${cashable_dollars:.2f})")
    except ValueError:
        print(f"Invalid cashable amount: {cashable_amount}")
    
    # Restricted Amount (5 bytes BCD)
    restricted_amount = command_hex[index:index+10]
    index += 10
    try:
        restricted_cents = int(restricted_amount, 16)
        restricted_dollars = restricted_cents / 100
        print(f"Restricted Amount: {restricted_amount} ({restricted_cents} cents = ${restricted_dollars:.2f})")
    except ValueError:
        print(f"Invalid restricted amount: {restricted_amount}")
    
    # Non-restricted Amount (5 bytes BCD)
    nonrestricted_amount = command_hex[index:index+10]
    index += 10
    try:
        nonrestricted_cents = int(nonrestricted_amount, 16)
        nonrestricted_dollars = nonrestricted_cents / 100
        print(f"Non-restricted Amount: {nonrestricted_amount} ({nonrestricted_cents} cents = ${nonrestricted_dollars:.2f})")
    except ValueError:
        print(f"Invalid non-restricted amount: {nonrestricted_amount}")
    
    # Transfer Flag (1 byte)
    transfer_flag = command_hex[index:index+2]
    index += 2
    flag_meanings = {
        "03": "Soft cashout mode",
        "07": "Hard cashout mode",
        "0F": "Hard cashout mode (cashout)"
    }
    print(f"Transfer Flag: {transfer_flag} ({flag_meanings.get(transfer_flag, 'Unknown')})")
    
    # Asset Number (4 bytes)
    asset_number = command_hex[index:index+8]
    index += 8
    print(f"Asset Number: {asset_number}")
    
    # Registration Key (20 bytes)
    registration_key = command_hex[index:index+40]
    index += 40
    print(f"Registration Key: {registration_key}")
    
    # Transaction ID Length (1 byte)
    if index < len(command_hex):
        txn_id_length_hex = command_hex[index:index+2]
        index += 2
        try:
            txn_id_length = int(txn_id_length_hex, 16)
            print(f"Transaction ID Length: {txn_id_length_hex} ({txn_id_length} bytes)")
            
            # Transaction ID (variable length)
            if txn_id_length > 0 and index + (txn_id_length * 2) <= len(command_hex):
                txn_id_hex = command_hex[index:index+(txn_id_length*2)]
                index += (txn_id_length * 2)
                
                # Decode transaction ID (it's ASCII encoded as hex)
                try:
                    txn_id_ascii = bytes.fromhex(txn_id_hex).decode('ascii')
                    print(f"Transaction ID: {txn_id_hex} (ASCII: '{txn_id_ascii}')")
                except:
                    print(f"Transaction ID: {txn_id_hex} (raw hex)")
        except ValueError:
            print(f"Invalid transaction ID length: {txn_id_length_hex}")
    
    # Expiration Date (4 bytes)
    if index + 8 <= len(command_hex):
        expiration_date = command_hex[index:index+8]
        index += 8
        print(f"Expiration Date: {expiration_date}")
    
    # Pool ID (2 bytes)
    if index + 4 <= len(command_hex):
        pool_id = command_hex[index:index+4]
        index += 4
        print(f"Pool ID: {pool_id}")
    
    # Receipt Data Length (1 byte)
    if index + 2 <= len(command_hex):
        receipt_length = command_hex[index:index+2]
        index += 2
        print(f"Receipt Data Length: {receipt_length}")
    
    # CRC (2 bytes at the end)
    if len(command_hex) >= 4:
        crc = command_hex[-4:]
        print(f"CRC: {crc}")
    
    print(f"=== End Analysis ===")

if __name__ == "__main__":
    # Analyze the command from the logs
    current_command = "01723900000A000002000000000000000000000000076C00000000000000000000000000000000000000000000000000043330383500000000000000568F"
    
    print("Analyzing current AFT command:")
    decode_aft_command(current_command)
    
    print("\n" + "="*80 + "\n")
    
    # Let's also analyze what a proper command should look like
    print("Expected command structure:")
    print("01 72 39 00 00 0A 00000200000000000000000000 07 6C000000 00000000000000000000000000000000000000000000000000000000000000000000000000000000 04 33303835 00000000 0000 00")
    print("^  ^  ^  ^  ^  ^  ^                           ^  ^        ^                                                                                  ^  ^        ^        ^    ^")
    print("A  C  L  TC TI TT Amounts (Cashable/Rest/Non) TF AssetNo  RegistrationKey                                                                    TL TxnID    ExpDate  Pool Rec") 