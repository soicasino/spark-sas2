# AFT (Advanced Funds Transfer) Improvements

## Overview

Based on analysis of the SAS protocol documentation and reference implementations, several key improvements have been made to the AFT system to address the issue where AFT commands were being sent but not processed by the machine.

## Key Issues Identified (Based on SAS Protocol Analysis & Gemini's Expert Review)

### 1. **Missing AFT Registration Method**

- The code referenced `komut_aft_registration()` but this method didn't exist
- Registration was falling back to manual command construction with potential format issues

### 2. **Improper AFT Registration Process**

- The SAS protocol requires a two-step registration process:
  1. Initialize registration (code FF - query status)
  2. Complete registration (code 01 + asset number + registration key + POS ID)
- Previous implementation jumped directly to step 2

### 3. **Asset Number Handling Issues**

- Asset numbers were hardcoded instead of being read from the machine
- The reference implementation shows asset numbers should be read dynamically using SAS command 73h

### 4. **✅ RESOLVED: BCD Encoding Investigation**

- **DISCOVERY**: Analysis of the original working code reveals it also doesn't do true BCD encoding
- The original `AddLeftBCD()` function just does string padding with zeros (same as our implementation)
- **CONCLUSION**: BCD encoding is NOT the issue - our current implementation matches the working original
- This rules out Gemini's BCD theory as the root cause

### 5. **Missing Response Handlers**

- AFT registration responses (73h) weren't being properly parsed
- Asset number conversion wasn't using the correct little-endian format
- Insufficient timeout periods for AFT operations
- Missing comprehensive status code parsing

## Improvements Made

### 1. **✅ VERIFIED: BCD Encoding Matches Original**

```python
def add_left_bcd(number_str, length_bytes):
    """
    Pads a number string with leading '00' to reach target byte length.
    This matches the original working implementation (AddLeftBCD + AddLeftString).

    Note: Despite the name "BCD", this function does NOT do true BCD encoding.
    It just does string padding, which is what the original working code did.
    """
```

**Impact**: Confirmed our implementation matches the original working code. BCD encoding is not the issue.

### 2. **Added Proper AFT Registration Method**

```python
def komut_aft_registration(self, assetnumber, registrationkey, posid):
    """
    Perform AFT registration with the gaming machine.
    This implements the proper two-step AFT registration process:
    1. Initialize registration (code FF - query status)
    2. Complete registration (code 01) with asset number, key, and POS ID
    """
```

### 2. **Added Asset Number Reading Method**

```python
def komut_read_asset_number(self):
    """
    Read the asset number from the gaming machine using SAS command 73h.
    This should be called at startup to get the machine's actual asset number.
    """
```

### 3. **Added AFT Registration Response Handler**

```python
def yanit_aft_registration(self, yanit):
    """
    Handle AFT registration response from the machine.
    This method parses the SAS 73h response and updates registration status.
    """
```

### 4. **Added Asset Number Conversion Utility**

```python
def read_asset_to_int(self, asset_hex):
    """
    Convert asset number from hex string to integer using little-endian format.
    This matches the reference implementation for asset number conversion.
    """
```

### 5. **Updated SAS Communicator**

- Modified `handle_received_sas_command()` to properly route AFT registration responses (73h)
- Added fallback to old asset number handling for compatibility

### 6. **Enhanced Registration Endpoints**

- Updated `/register-aft` endpoint to first read asset number from machine
- Improved logging and error handling throughout the registration process

## Testing Instructions

### 1. **Run the Test Script**

```bash
python test_aft_registration.py
```

This script will:

- Check current AFT debug status
- Perform AFT registration
- Verify registration success
- Test a small credit transfer

### 2. **Manual Testing Steps**

1. **Check AFT Debug Status**

   ```bash
   curl http://localhost:8000/api/money/aft-debug
   ```

2. **Perform AFT Registration**

   ```bash
   curl -X POST http://localhost:8000/api/money/register-aft
   ```

3. **Test Credit Transfer**

   ```bash
   curl -X POST http://localhost:8000/api/money/add-credits \
     -H "Content-Type: application/json" \
     -d '{"amount": 10.0, "transfer_type": "10"}'
   ```

4. **Check Balance**
   ```bash
   curl http://localhost:8000/api/money/balance
   ```

### 3. **Expected Results**

After proper AFT registration:

- AFT status should change from "80" (Not Registered) to "01" (Registered)
- Asset number should be read from the machine (not hardcoded)
- Credit transfers should receive proper responses instead of timeouts
- Machine should actually process the transfers and update balances

## Key Differences from Reference Implementation

### 1. **Registration Process**

- **Reference**: Uses two separate commands (initialize + complete)
- **Our Implementation**: Now matches this pattern

### 2. **Asset Number Handling**

- **Reference**: Reads asset number dynamically and stores it
- **Our Implementation**: Now reads asset number before registration

### 3. **Response Parsing**

- **Reference**: Comprehensive parsing of all AFT response fields
- **Our Implementation**: Now includes proper AFT registration response parsing

## Debugging Tips

### 1. **Check Logs**

Look for these log messages:

- `[AFT REGISTRATION] Starting AFT registration process`
- `[AFT REG RESPONSE] Received AFT registration response`
- `[ASSET NUMBER] Reading asset number from machine`

### 2. **Common Issues**

- **Status "80"**: Machine not registered - run registration
- **Status "81"**: Registration key mismatch - check asset number format
- **Status "82"**: No POS ID - check registration parameters
- **No response**: Machine may not support AFT or communication issues

### 3. **Verification Steps**

1. Confirm asset number is read from machine (not hardcoded "0000006C")
2. Verify registration status changes to "01" after registration
3. Check that transfers receive responses instead of timeouts
4. Confirm machine actually processes transfers (balance changes)

## Next Steps

If AFT transfers still don't work after these improvements:

1. **Check Machine AFT Support**: Verify the machine actually supports AFT
2. **Analyze Protocol Differences**: Compare command formats with working old app
3. **Registration Key**: Try different registration keys if default doesn't work
4. **Asset Number Format**: Verify the asset number format matches machine expectations
5. **Timing Issues**: Adjust delays between registration steps if needed

The key insight from the reference implementation is that AFT registration is a critical prerequisite that must be done correctly before any transfers will be processed by the machine.
