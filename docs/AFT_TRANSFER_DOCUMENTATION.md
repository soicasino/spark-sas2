# AFT (Automated Funds Transfer) Implementation Documentation

## Overview

This document describes how AFT operations work in the original SAS (Slot Accounting System) casino implementation. AFT enables automated money transfers between the host system and gaming machines using the SAS protocol.

## Table of Contents

1. [AFT Transfer Flow](#aft-transfer-flow)
2. [Command Construction](#command-construction)
3. [Polling Mechanism](#polling-mechanism)
4. [Response Handling](#response-handling)
5. [Status Codes](#status-codes)
6. [Error Handling](#error-handling)
7. [Configuration](#configuration)

---

## AFT Transfer Flow

### 1. **Initiation Phase**

```
Host System → Gaming Machine
- Constructs AFT command (SAS 72h)
- Includes transaction details, amounts, asset info
- Sends command during polling cycle
```

### 2. **Processing Phase**

```
Gaming Machine Processing:
- Validates transaction ID uniqueness
- Checks registration key match
- Verifies asset number
- Processes amount transfer
- Updates internal balance
```

### 3. **Response Phase**

```
Gaming Machine → Host System
- Returns AFT response (SAS 72h response)
- Includes transfer status code
- Provides transaction confirmation
- Updates balance information
```

### 4. **Completion Phase**

```
Final Confirmation:
- AFT completion notification (FF69)
- Balance verification (SAS 74h)
- Transaction logging
- Status updates
```

---

## Command Construction

### AFT Command Structure (SAS 72h)

The AFT command is built using the `Komut_ParaYukle()` function:

```python
def Komut_ParaYukle(doincreasetransactionid, transfertype):
    # Command Header
    CommandHeader = Config.get("sas","address")    # "01" - Machine Address
    CommandHeader += "72"                          # SAS Command 72h (AFT)
    CommandHeader += ""                            # Length (calculated later)

    # Command Body
    Command = ""
    Command += "00"                                # Transfer Code (00=credit)
    Command += "00"                                # Transfer Index
    Command += "00"                                # Transfer Type (00=cashable, 10/11=bonus)

    # Amount Fields (BCD Format - 5 bytes each)
    Command += AddLeftBCD(customerbalanceint, 5)   # Cashable Amount
    Command += AddLeftBCD(int(customerpromo*100), 5) # Restricted Amount
    Command += "0000000000"                        # Non-restricted Amount

    # Transfer Settings
    Command += "07"                                # Transfer Flag (07=hard cashout)
    Command += Config.get("sas","assetnumber")     # Asset Number (4 bytes)
    Command += Config.get("sas","registrationkey") # Registration Key (20 bytes)

    # Transaction Details
    TRANSACTIONID = "".join("{:02x}".format(ord(c)) for c in str(transactionid))
    Command += AddLeftBCD(int(len(TRANSACTIONID)/2), 1)  # Transaction ID Length
    Command += TRANSACTIONID                             # Transaction ID
    Command += "00000000"                               # Expiration Date
    Command += "0000"                                   # Pool ID
    Command += "00"                                     # Receipt Data Length

    # Finalize Command
    CommandHeader += hex(int(len(Command)/2)).replace("0x","")  # Add length
    GenelKomut = CommandHeader + Command
    GenelKomut = GetCRC(GenelKomut)                            # Add CRC

    # Send Command
    SAS_SendCommand("ParaYukle", GenelKomut, 1)
```

### Key Components Explained

| Component             | Size        | Description       | Example               |
| --------------------- | ----------- | ----------------- | --------------------- |
| **Address**           | 1 byte      | Machine address   | `01`                  |
| **Command**           | 1 byte      | AFT command code  | `72`                  |
| **Length**            | 1 byte      | Command length    | `35`                  |
| **Transfer Code**     | 1 byte      | Transfer type     | `00` (credit)         |
| **Transfer Index**    | 1 byte      | Transfer sequence | `00`                  |
| **Transfer Type**     | 1 byte      | Money type        | `00` (cashable)       |
| **Cashable Amount**   | 5 bytes BCD | Main amount       | `0000050000` (500.00) |
| **Restricted Amount** | 5 bytes BCD | Promo/bonus       | `0000000000`          |
| **Non-restricted**    | 5 bytes BCD | Non-cashable      | `0000000000`          |
| **Transfer Flag**     | 1 byte      | Cashout mode      | `07` (hard)           |
| **Asset Number**      | 4 bytes     | Machine ID        | `6C000000`            |
| **Registration Key**  | 20 bytes    | Security key      | `000...000`           |
| **Transaction ID**    | Variable    | Unique ID         | `31323334`            |
| **CRC**               | 2 bytes     | Checksum          | `99EA`                |

---

## Polling Mechanism

### Original Polling Logic

The SAS communication uses a continuous polling mechanism:

```python
def DoSASPooling():
    while True:
        # Alternate between General Poll (80h) and Interrogation (81h)
        if Sas_LastSent == 80 and Send81 == 1 and DoPolling == 1:
            SendSASCommand("81")  # Interrogation
            Sas_LastSent = 81
        else:
            SendSASCommand("80")  # General Poll
            Sas_LastSent = 80

        time.sleep(0.02)  # 20ms between polls

        # Read responses
        tdata = GetDataFromSasPort(IsMessageSent)
        if tdata:
            ProcessSASMessage(tdata)
```

### Polling Commands

| Command           | Hex  | Purpose              | Frequency        |
| ----------------- | ---- | -------------------- | ---------------- |
| **General Poll**  | `80` | Request pending data | Every other poll |
| **Interrogation** | `81` | Status inquiry       | Every other poll |

### Timing Requirements

- **Poll Interval**: 20ms between commands
- **Response Timeout**: 100ms maximum
- **Inter-byte Delay**: 5ms for multi-byte responses
- **Command Delay**: 30-90ms after AFT commands

---

## Response Handling

### AFT Response Processing

AFT responses are detected and parsed by `Yanit_ParaYukle()`:

```python
def Yanit_ParaYukle(Yanit):
    # Parse Response Structure
    index = 0
    Address = Yanit[index:index+2]          # Machine address
    index += 2
    Command = Yanit[index:index+2]          # Command (72)
    index += 2
    Length = Yanit[index:index+2]           # Response length
    index += 2
    TransactionBuffer = Yanit[index:index+2] # Buffer number
    index += 2
    TransferStatus = Yanit[index:index+2]   # *** CRITICAL: Transfer status ***
    index += 2

    # Process Transfer Status
    if TransferStatus == "00":
        print("AFT Transfer Successful!")
        IsWaitingForParaYukle = 0
    elif TransferStatus == "C0":
        print("AFT Transfer Acknowledged - Processing...")
    else:
        print(f"AFT Transfer Failed: Status {TransferStatus}")
```

### Response Detection Logic

The main message processing loop detects AFT responses:

```python
# In main polling loop
if tdata[0:4] == "0172":  # AFT Response detected
    if tdata[12:14] == "00" or tdata[12:14] == "10" or tdata[12:14] == "11":
        # Success responses for cash-in
        Yanit_ParaYukle(tdata)
    elif tdata[12:14] == "80" or tdata[12:14] == "90":
        # Cash-out responses
        Yanit_ParaSifirla(tdata)

# AFT Completion Notification
if tdata.startswith("01FF69DB5B") or tdata == "69":
    print("AFT Transfer is completed")
    # Final completion processing
```

---

## Status Codes

### Transfer Status Codes (Position 12-13 in response)

| Code   | Description                      | Action Required           |
| ------ | -------------------------------- | ------------------------- |
| **00** | ✅ **Transfer successful**       | Complete transaction      |
| **10** | ✅ **Bonus/Jackpot successful**  | Complete transaction      |
| **11** | ✅ **Jackpot successful**        | Complete transaction      |
| **40** | ⏳ **Transfer pending**          | Wait for completion       |
| **C0** | ⏳ **Transfer acknowledged**     | Continue waiting          |
| **81** | ❌ **Transaction ID not unique** | Generate new ID           |
| **82** | ❌ **Registration key mismatch** | Check configuration       |
| **83** | ❌ **Invalid transfer function** | Check command format      |
| **84** | ❌ **Amount exceeds limit**      | Reduce transfer amount    |
| **85** | ❌ **Denomination incompatible** | Check machine settings    |
| **87** | ❌ **Machine unable to accept**  | Check machine status      |
| **89** | ❌ **Registration key invalid**  | Update registration       |
| **93** | ❌ **Asset number mismatch**     | Check asset configuration |
| **94** | ❌ **Machine not locked**        | Lock machine first        |
| **C1** | ❌ **Unsupported transfer code** | Check command structure   |
| **FF** | ❌ **General transfer failure**  | Retry or investigate      |

### Completion Notifications

| Response       | Meaning                       | Next Action          |
| -------------- | ----------------------------- | -------------------- |
| **FF69DB5B**   | AFT operation completed       | Verify balance       |
| **69**         | Short completion notification | Continue polling     |
| **01FF69DB5B** | Full completion with header   | Transaction finished |

---

## Error Handling

### Retry Logic

The original system implements sophisticated retry mechanisms:

```python
# Transaction ID Conflict (Status 81)
if TransferStatus == "81":
    transactionid += 1
    if transactionid > 1000:
        transactionid = 1
    # Retry with new transaction ID

# Machine Disabled (Status 87)
if TransferStatus == "87":
    SQL_InsImportantMessageByWarningType(
        "Door is opened, slot tilt or disabled! Can't upload money!", 1, 5
    )
    # Wait for machine to become available

# Asset Number Mismatch (Status 93)
if TransferStatus == "93":
    Komut_ReadAssetNo()  # Re-read asset number
    Wait_Bakiye(11, 1, "asset")  # Check balance
    # Update configuration and retry
```

### Timeout Handling

```python
# AFT Response Timeout
if not aft_response_received and time_elapsed > 30:
    print("AFT operation timed out")
    # Log failure and retry or abort

# Polling Timeout
if no_response_for > 5_seconds:
    # Restart polling
    # Check serial connection
    # Reset communication
```

---

## Configuration

### Required Settings

```ini
[sas]
address=01                    # Machine address (hex)
assetnumber=6C000000         # Asset number (4 bytes hex)
registrationkey=000000...000  # Registration key (40 hex chars)

[payment]
transactionid=1              # Current transaction ID counter

[customer]
customerbalance=100.50       # Amount to transfer
customerpromo=0.00          # Promotional amount
```

### BCD Format Functions

```python
def AddLeftBCD(numbers, length):
    """Convert number to BCD format with specified byte length"""
    numbers = int(numbers)
    retdata = str(numbers)

    # Ensure even number of digits
    if len(retdata) % 2 == 1:
        retdata = "0" + retdata

    # Calculate padding needed
    countNumber = len(retdata) / 2
    kalan = int(length - countNumber)

    # Add leading zeros
    retdata = AddLeftString(retdata, "00", kalan)
    return retdata

def AddLeftString(text, eklenecek, kacadet):
    """Add string to left side specified number of times"""
    while kacadet > 0:
        text = eklenecek + text
        kacadet = kacadet - 1
    return text
```

### CRC Calculation

```python
def GetCRC(command):
    """Calculate SAS CRC-16 Kermit for command"""
    try:
        data = bytearray.fromhex(command)
        crc_instance = CrcKermit()
        crc_instance.process(data)
        crc_hex = crc_instance.finalbytes().hex().upper()
        crc_hex = crc_hex.zfill(4)
        # SAS requires CRC bytes reversed
        return command + crc_hex[2:4] + crc_hex[0:2]
    except Exception as e:
        return command + "0000"
```

---

## Example AFT Transaction

### Complete Transaction Flow

```
1. COMMAND CONSTRUCTION:
   Address: 01
   Command: 72
   Length: 35
   Transfer Code: 00
   Amount: 0000050000 (500.00 in BCD)
   Asset: 6C000000
   Transaction ID: 31323334 ("1234")
   Final: 017235000000000005000000000000000000000000076C000000...99EA

2. POLLING SEQUENCE:
   TX: 0180A5C0 (General Poll)
   RX: 00 (No data)
   TX: 0181598C (Interrogation)
   RX: 00 (No data)
   TX: 017235... (AFT Command)
   RX: 01 (ACK)

3. RESPONSE PROCESSING:
   TX: 0180A5C0 (Poll for response)
   RX: 017235000000C0... (AFT Response - Status C0: Acknowledged)
   TX: 0180A5C0 (Continue polling)
   RX: 017235000000000... (AFT Response - Status 00: Success)

4. COMPLETION:
   TX: 0180A5C0 (Poll)
   RX: 69 (AFT Completion notification)

5. VERIFICATION:
   TX: 017400000000CRC (Balance Query)
   RX: 0174...0000050000... (Balance: 500.00 confirmed)
```

### Transaction States

```
IDLE → COMMAND_SENT → ACKNOWLEDGED → PROCESSING → COMPLETED → VERIFIED
  ↓         ↓              ↓            ↓           ↓          ↓
 Ready   Waiting      Processing    Success     Finished   Confirmed
```

---

## Best Practices

### 1. **Transaction ID Management**

- Always increment transaction IDs
- Handle rollover at 1000
- Ensure uniqueness within session

### 2. **Error Recovery**

- Implement exponential backoff for retries
- Log all failures for analysis
- Provide user feedback for common errors

### 3. **Timing Considerations**

- Respect minimum polling intervals
- Allow adequate response timeouts
- Handle machine processing delays

### 4. **Security**

- Validate all response data
- Verify CRC checksums
- Maintain audit trails

### 5. **Monitoring**

- Track success/failure rates
- Monitor response times
- Alert on repeated failures

---

## Troubleshooting Guide

### Common Issues

| Problem            | Symptoms                   | Solution                   |
| ------------------ | -------------------------- | -------------------------- |
| **No Response**    | Command sent, no reply     | Check polling mechanism    |
| **Status 81**      | Transaction ID conflict    | Increment transaction ID   |
| **Status 87**      | Machine disabled           | Check door/tilt status     |
| **Status C0 Loop** | Stuck in acknowledged      | Wait longer, check machine |
| **CRC Errors**     | Invalid responses          | Check serial communication |
| **Timeout**        | No completion notification | Verify polling continues   |

### Debug Steps

1. **Verify Serial Communication**

   - Check port settings (19200, 8N1)
   - Confirm hardware connections
   - Test basic polling (80/81)

2. **Validate Command Construction**

   - Check BCD formatting
   - Verify CRC calculation
   - Confirm asset/registration match

3. **Monitor Polling Loop**

   - Ensure continuous polling
   - Check response parsing
   - Verify timing intervals

4. **Analyze Responses**
   - Log all SAS messages
   - Parse status codes correctly
   - Track transaction states

---

_This documentation is based on analysis of the original SAS casino system implementation and provides a comprehensive guide to AFT transfer operations._
